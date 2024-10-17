# przycina wszystkie warstwy we wskazanej lokalizacji
# wg aoi nie zmieniajac ich nazw, ani struktury tabeli atrubutó

def clip_shapefiles(self):
    # Define paths
    input_directory = "D:/22_mapa_utrudnien/warstwy/bdot10k_Polska_SHP/06_SHP"
    output_directory = "D:/22_mapa_utrudnien/warstwy/bdot10k_Polska_SHP/aaaa"
    aoi_path = "D:/22_mapa_utrudnien/granica_wschód_buff30.shp"

    # Load the AOI shapefile
    aoi_layer = QgsVectorLayer(aoi_path, "AOI", "ogr")
    if not aoi_layer.isValid():
        print("AOI layer is not valid.")
        return

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Loop through each shapefile in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith(".shp"):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)

            try:
                # Load the input shapefile as a QGIS layer
                input_layer = QgsVectorLayer(input_path, "input_layer", "ogr")

                # Check for valid layer
                if not input_layer.isValid():
                    print(f"Layer {filename} is not valid.")
                    continue

                # Fix geometries using QGIS processing
                params = {
                    'INPUT': QgsProcessingFeatureSourceDefinition(input_path, selectedFeaturesOnly=False,
                                                                  featureLimit=-1,
                                                                  geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                    'OUTPUT': 'memory:'
                }
                result = processing.run('native:fixgeometries', params)

                fixed_layer = result['OUTPUT']

                # Clip the shapefile using the AOI
                clip_params = {
                    'INPUT': fixed_layer,
                    'OVERLAY': aoi_layer,
                    'OUTPUT': 'memory:'
                }
                clip_result = processing.run('native:clip', clip_params)

                clipped_layer = clip_result['OUTPUT']

                # Save the clipped shapefile to the output directory
                error = QgsVectorFileWriter.writeAsVectorFormat(clipped_layer, output_path, "utf-8",
                                                                clipped_layer.crs(), "ESRI Shapefile")
                if error != QgsVectorFileWriter.NoError:
                    print(f"Error saving {filename}: {error}")

                print(f"Clipped {filename} and saved to {output_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")


    # analiza zalewania na urzadzeniach piętrzących

    def calculate_inundation_area(self, dtm_path, dam_height, transform):
        """Calculate the area inundated by water up to a given height, handling large rasters."""
        inundation_polygons = []
        with rasterio.open(dtm_path) as src:
            width = src.width
            height = src.height
            block_size = 512  # Define block size (adjust based on memory capacity)

            for row_start in range(0, height, block_size):
                row_end = min(row_start + block_size, height)
                for col_start in range(0, width, block_size):
                    col_end = min(col_start + block_size, width)
                    window = Window(col_start, row_start, col_end - col_start, row_end - row_start)

                    # Read data in chunks
                    dtm_array = src.read(1, window=window)

                    # Create binary mask
                    water_mask = dtm_array <= dam_height

                    # Convert mask to polygons
                    shapes = rasterio.features.shapes(water_mask.astype(np.uint8), transform=src.window_transform(window))
                    polygons = [Polygon(shape[0]['coordinates'][0]) for shape in shapes if shape[1] > 0]
                    inundation_polygons.extend(polygons)

        # Combine polygons into a single geometry
        inundation_area = unary_union(inundation_polygons)
        return inundation_area

    def divide_watershed(self, watershed, dam_location, dtm_path):
        """Divide the watershed into upstream and downstream parts using a consistent line perpendicular to the main flow direction."""

        def calculate_dominant_flow_direction(watershed, src):
            """Estimate the dominant flow direction across the entire watershed."""
            minx, miny, maxx, maxy = watershed.bounds
            x_coords = np.linspace(minx, maxx, num=10)
            y_coords = np.linspace(miny, maxy, num=10)
            directions = []

            for x in x_coords:
                for y in y_coords:
                    point = Point(x, y)
                    delta = 1  # Small distance to calculate gradient
                    elevations = {}
                    for dx in [-delta, 0, delta]:
                        for dy in [-delta, 0, delta]:
                            sample_x, sample_y = x + dx * delta, y + dy * delta
                            samples = list(src.sample([(sample_x, sample_y)]))
                            if samples:
                                elevations[(dx, dy)] = samples[0][0]

                    if len(elevations) >= 4:
                        gradient_x = (elevations[(delta, 0)] - elevations[(-delta, 0)]) / (2 * delta)
                        gradient_y = (elevations[(0, delta)] - elevations[(0, -delta)]) / (2 * delta)
                        angle = np.arctan2(gradient_y, gradient_x)
                        directions.append(angle)

            if not directions:
                raise ValueError("Could not determine dominant flow direction.")

            # Compute the dominant flow direction
            dominant_direction = np.mean(directions)
            return dominant_direction

        def create_perpendicular_line(point, angle, length):
            """Create a line perpendicular to the given angle at the point."""
            angle_perpendicular = angle + np.pi / 2  # Perpendicular angle
            x1 = point.x + length * np.cos(angle_perpendicular)
            y1 = point.y + length * np.sin(angle_perpendicular)
            x2 = point.x - length * np.cos(angle_perpendicular)
            y2 = point.y - length * np.sin(angle_perpendicular)
            return LineString([(x1, y1), (x2, y2)])

        # Determine the dominant flow direction for the entire watershed
        with rasterio.open(dtm_path) as src:
            flow_direction = calculate_dominant_flow_direction(watershed, src)
            if flow_direction is None:
                raise ValueError("Could not determine flow direction.")

        # Create a line through the dam location and perpendicular to the dominant flow direction
        minx, miny, maxx, maxy = watershed.bounds
        max_distance = max(dam_location.distance(Point(minx, miny)),
                           dam_location.distance(Point(minx, maxy)),
                           dam_location.distance(Point(maxx, miny)),
                           dam_location.distance(Point(maxx, maxy))) + 1  # Add 1 meter buffer

        dam_line = create_perpendicular_line(dam_location, flow_direction, max_distance)

        print(f"Dam Line: {dam_line}")

        # Split the watershed using the perpendicular dam line
        split_result = split(watershed, dam_line)

        print(f"Split Result: {split_result}")

        # Handle split result as MultiPolygon
        if isinstance(split_result, GeometryCollection):
            split_result = MultiPolygon([geom for geom in split_result.geoms if isinstance(geom, Polygon)])
        elif isinstance(split_result, Polygon):
            split_result = MultiPolygon([split_result])
        else:
            split_result = MultiPolygon([geom for geom in split_result if isinstance(geom, Polygon)])

        # Check number of polygons resulting from split
        if len(split_result.geoms) > 2:
            print(
                f"Warning: The split resulted in more than two polygons. Number of polygons: {len(split_result.geoms)}")
            polygons = sorted(split_result.geoms, key=lambda p: p.area, reverse=True)[:2]
        else:
            polygons = list(split_result.geoms)

        if len(polygons) != 2:
            raise ValueError(
                "The watershed was not split into exactly two parts. Number of resulting polygons: {}".format(
                    len(polygons)))

        # Calculate mean elevation for each polygon
        def calculate_mean_elevation(polygon, src):
            """Calculate the mean elevation within a polygon."""
            elevations = []
            for x, y in polygon.exterior.coords:
                sample = list(src.sample([(x, y)]))  # Convert generator to list
                if sample:
                    elevation = sample[0][0]
                    if elevation is not None:
                        elevations.append(elevation)
            return np.mean(elevations) if elevations else float('nan')

        def is_polygon_upstream(polygon, flow_direction):
            """Determine if a polygon is upstream based on its orientation relative to flow direction."""
            centroid = polygon.centroid
            angle_to_flow = np.arctan2(centroid.y - dam_location.y, centroid.x - dam_location.x)
            angle_diff = np.abs(np.angle(np.exp(1j * (flow_direction - angle_to_flow))))
            return angle_diff < np.pi / 2  # Within 90 degrees of flow direction

        with rasterio.open(dtm_path) as src:
            mean_elevations = []
            for polygon in polygons:
                mean_elevations.append(calculate_mean_elevation(polygon, src))

            # Determine which polygon has the higher mean elevation
            if len(mean_elevations) != 2:
                raise ValueError("Error in calculating mean elevations.")

            # Classify polygons based on both mean elevation and flow direction
            if is_polygon_upstream(polygons[0], flow_direction):
                upstream, downstream = polygons[0], polygons[1]
            else:
                upstream, downstream = polygons[1], polygons[0]

        return upstream, downstream

    def clip_with_buffer(self, inundation_area, dam_location, buffer_distance):
        """Clip the inundation area with a buffer around the dam location."""
        buffer = dam_location.buffer(buffer_distance)
        return inundation_area.intersection(buffer)

    def process_dams(self, dams_shapefile, dtm_path, height_field, id_field, output_dir, watersheds_shapefile):
        dams_gdf = gpd.read_file(dams_shapefile)
        watersheds_gdf = gpd.read_file(watersheds_shapefile)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with rasterio.open(dtm_path) as src:
            transform = src.transform
            crs = src.crs

        for idx, dam in dams_gdf.iterrows():
            dam_id = dam[id_field]
            dam_height = dam[height_field]
            dam_location = dam.geometry

            # Find the corresponding watershed
            watershed = watersheds_gdf[watersheds_gdf.contains(dam_location)].geometry.iloc[0]

            # Divide the watershed into upstream and downstream parts
            upstream, downstream = self.divide_watershed(watershed, dam_location, dtm_path)

            # Calculate inundation area
            inundation_area = self.calculate_inundation_area(dtm_path, dam_height, transform)

            # Create buffer of 2.5 km around the dam
            dam_buffer = dam_location.buffer(2500)

            # Clip inundation area with the buffer
            inundation_area_clipped = inundation_area.intersection(dam_buffer)

            # Clip the buffered inundation area with the upstream polygon
            inundation_area_upstream = inundation_area_clipped.intersection(upstream)

            # Convert multi-part geometries to single-part
            inundation_parts = [geom for geom in inundation_area_upstream.geoms] if isinstance(inundation_area_upstream,
                                                                                               MultiPolygon) else [
                inundation_area_upstream]

            # Filter geometries within a 100-meter radius of the dam location
            final_inundation_geometries = [geom for geom in inundation_parts if dam_location.distance(geom) <= 100]

            # Save the inundation area and divided watersheds to shapefiles
            schema = {'geometry': 'Polygon', 'properties': {id_field: 'str'}}

            final_inundation_shapefile = os.path.join(output_dir, f'dam_{dam_id}_inundation_final.shp')
            with fiona.open(final_inundation_shapefile, 'w', driver='ESRI Shapefile', schema=schema, crs=crs) as output:
                for geom in final_inundation_geometries:
                    output.write({'geometry': geom.__geo_interface__, 'properties': {id_field: str(dam_id)}})

            upstream_shapefile = os.path.join(output_dir, f'dam_{dam_id}_upstream.shp')
            downstream_shapefile = os.path.join(output_dir, f'dam_{dam_id}_downstream.shp')

            with fiona.open(upstream_shapefile, 'w', driver='ESRI Shapefile', schema=schema, crs=crs) as output:
                output.write({'geometry': upstream.__geo_interface__, 'properties': {id_field: str(dam_id)}})

            with fiona.open(downstream_shapefile, 'w', driver='ESRI Shapefile', schema=schema, crs=crs) as output:
                output.write({'geometry': downstream.__geo_interface__, 'properties': {id_field: str(dam_id)}})

    def run_inundation_analysis(self):
        dams_shapefile = 'D:/0204/budowle_małej_retencji_brzeg.shp'
        dtm_path = 'D:/0204/nmt1m/NMT_Kafle/NMT.tif'
        height_field = 'teo_rz_p_6'
        id_field = 'nr_roboczy'
        output_dir = 'D:/0204/anal_zalew'
        watersheds_shapefile = 'D:/0204/anal_zalew/zlew_5.shp'

        try:
            self.process_dams(dams_shapefile, dtm_path, height_field, id_field, output_dir, watersheds_shapefile)
            QMessageBox.information(self.iface.mainWindow(), 'Success', 'Inundation analysis completed successfully.')
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), 'Error', f'An error occurred: {str(e)}')

    #         zwraca dane z osm, tutaj jeszcze problem z odwzorowaniem, mozna spróbowa 4283 czy jakos tak
    def fetch_and_save_osm_data(self):
        lat = 51.1078852
        lon = 17.0385376
        radius_km = 10
        output_path = "D:\\23_data\\wroclaw_osm_data.gpkg"

        def fetch_osm_data(lat, lon, radius_km):
            overpass_url = "http://overpass-api.de/api/interpreter"
            overpass_query = f"""
            [out:json];
            (
              node(around:{radius_km * 1000},{lat},{lon});
              way(around:{radius_km * 1000},{lat},{lon});
              relation(around:{radius_km * 1000},{lat},{lon});
            );
            out body;
            >;
            out skel qt;
            """
            response = requests.get(overpass_url, params={'data': overpass_query})
            data = response.json()
            return data

        def parse_osm_data(osm_data):
            nodes = {node['id']: (node['lat'], node['lon']) for node in osm_data['elements'] if node['type'] == 'node'}
            geometries = []

            for element in osm_data['elements']:
                if element['type'] == 'node':
                    point = Point(nodes[element['id']])
                    geometries.append({'type': 'node', 'geometry': point, 'properties': element})
                elif element['type'] == 'way':
                    line = LineString([nodes[node_id] for node_id in element['nodes']])
                    geometries.append({'type': 'way', 'geometry': line, 'properties': element})
                elif element['type'] == 'relation' and 'members' in element:
                    poly_nodes = []
                    for member in element['members']:
                        if member['type'] == 'node':
                            poly_nodes.append(nodes[member['ref']])
                    if len(poly_nodes) >= 4:  # Ensure there are at least 4 coordinates
                        polygon = Polygon(poly_nodes)
                        geometries.append({'type': 'relation', 'geometry': polygon, 'properties': element})

            return geometries

        def save_to_spatial_file(geometries, output_path):
            gdf = gpd.GeoDataFrame(geometries)
            gdf.set_crs(epsg=2180, inplace=True)
            gdf.to_file(output_path, driver="GPKG")

        osm_data = fetch_osm_data(lat, lon, radius_km)
        geometries = parse_osm_data(osm_data)
        save_to_spatial_file(geometries, output_path)
        print(f"Data saved to {output_path}")

# export tabeli z bazy accesowej

def export_all_tables_to_csv(self):
    """
    Export all tables from an Access database (.mdb) to CSV files using COM interface.
    """
    db_path = r'D:\mSWPS\szablonBS.mdb'  # Path to the Access database file
    export_path = r'D:\mSWPS\TABELE'  # Directory path where CSV files will be saved

    # Ensure export path exists
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    # Create Access application object
    access_app = win32com.client.Dispatch("Access.Application")
    access_app.Visible = False  # Optional: keep Access invisible

    try:
        # Open the database
        db = access_app.DBEngine.OpenDatabase(db_path)

        # Get list of tables
        table_defs = db.TableDefs

        for table in table_defs:
            table_name = table.Name
            print(f'Exporting table: {table_name}')

            # Use DAO to open the table and read data
            dao_db = access_app.DBEngine.OpenDatabase(db_path)
            dao_table = dao_db.TableDefs[table_name]
            recordset = dao_table.OpenRecordset()

            # Create a list to hold the rows
            rows = []

            # Get column headers
            columns = [field.Name for field in recordset.Fields]

            # Check if the recordset contains records
            if recordset.RecordCount > 0:
                recordset.MoveFirst()  # Move to the first record

                while not recordset.EOF:
                    row = []
                    for field in recordset.Fields:
                        row.append(field.Value)
                    rows.append(row)
                    recordset.MoveNext()  # Move to the next record

            else:
                print(f"Table {table_name} is empty. Exporting structure only.")

            # Create a pandas DataFrame to hold the data (even if it's empty)
            df = pd.DataFrame(rows, columns=columns)

            # Export DataFrame to CSV
            csv_file_path = os.path.join(export_path, f'{table_name}.csv')
            df.to_csv(csv_file_path, index=False, sep=';')  # Use semicolon as delimiter

            # Clean up
            recordset.Close()
            dao_db.Close()

        print("Export completed!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        access_app.Quit()
        del access_app


