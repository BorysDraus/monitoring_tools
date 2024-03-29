import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox, QWidget
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QLineEdit, QToolBar, QProgressDialog
from qgis.core import QgsProject, Qgis, QgsVectorLayer, QgsProcessingFeedback,  QgsFields, QgsCoordinateReferenceSystem
from qgis._core import QgsWkbTypes, QgsMapLayer, QgsVectorFileWriter, QgsVectorDataProvider, QgsField, QgsRectangle, QgsMapLayerProxyModel, QgsProcessing
from qgis.core import *
from .TimerMessageBox import CustomMessageBox
# from qgis.gui import QProgressDialog

class AtributeTableManager():


    # Metoda przepisująca wartości pomiędzy kolumnami we wskazanej warstwie
    def rewriteDataFromColumn(self, layerName, columnFrom, columnTo):

        layer = QgsProject.instance().mapLayersByName(layerName)[0]
        layer_provider = layer.dataProvider()

        field_from = layer.fields().indexFromName(columnFrom)
        field_target = layer.fields().indexFromName(columnTo)

        for features in layer.getFeatures():
            id = features.id()
            feature = layer.getFeature(id)

            value = feature[field_from] or 0

            attr_to = {field_target: value}
            layer_provider.changeAttributeValues({id: attr_to})

        layer.commitChanges()


    def rewriteDataBetweenLayers(self, layerSource, layerTarget, column_to_rewrite_name, column_ID_layer_source_name, column_ID_layer_target_name):


        # layer_source_provider = layerSource.dataProvider()
        # layer_target_provider = layerTarget.dataProvider()

        field_rewrite_from = layerSource.fields().indexFromName(column_to_rewrite_name)
        field_id_source = layerSource.fields().indexFromName(column_ID_layer_source_name)
        field_id_target = layerTarget.fields().indexFromName(column_ID_layer_target_name)

        # Check if the column exists
        if field_rewrite_from != -1:
            # Get the field (column) object
            field = layerSource.fields().field(field_rewrite_from)
            # Get the data type of the field
            data_type = field.typeName()
            print(str(data_type))

        # Add column to table
        layerTarget.startEditing()
        layer_provider = layerTarget.dataProvider()
        field_index = layerTarget.fields().indexFromName(column_to_rewrite_name)
        if field_index == -1:
            layer_provider.addAttributes([QgsField(column_to_rewrite_name, dataType)])
        try:
            layerTarget.updateFields()
        except:
            CustomMessageBox.showWithTimeout(5, "Nie dodano nowych kolumn! Sprawdź tabelę atrybutów", "", icon=QMessageBox.Warning)
        layerTarget.commitChanges()
        layerTarget.updateExtents()
        field_rewrite_to = layerTarget.fields().indexFromName(column_to_rewrite_name)


        # TST
        # total_features = layerTarget.featureCount()
        # # Create a progress dialog
        # progress_dialog = QProgressDialog("Processing...", "Cancel", 0, total_features)
        # progress_dialog.setWindowModality(Qt.WindowModal)
        # progress_dialog.setWindowTitle("My Plugin")
        # progress_dialog.show()

        total_features = layerSource.featureCount()
        layer_provider = layerTarget.dataProvider()

        progress_dialog = QProgressDialog("Processing...", "Cancel", 0, total_features)
        progress_dialog.setWindowModality(2)  # Make the dialog modal
        progress_dialog.show()

        # Loop through layerTarget
        for targetFeatures in layerTarget.getFeatures():
            id_target = targetFeatures.id()
            feat_target = layerTarget.getFeature(id_target)
            join_id_number_target = feat_target[field_id_target]

            progress_dialog.setValue(id_target)
            # i = i + 1

            for sourceFeatures in layerSource.getFeatures():
                id_source = sourceFeatures.id()
                feat_source = layerSource.getFeature(id_source)
                join_id_number_source = feat_source[field_id_source]
                value_to_rewrite = feat_source[field_rewrite_from] or 0

                if join_id_number_target == join_id_number_source:
                    attr_to = {field_rewrite_to: value_to_rewrite}
                    layer_provider.changeAttributeValues({id_target: attr_to})

                # Update progress
                # progress_dialog.setValue(i)

        layerTarget.commitChanges()
        progress_dialog.setValue(total_features)
        progress_dialog.close()


        # QgsApplication.processEvents()
        #
        # progress_dialog.close()


    # Metoda zmieniająca nazwę kolumny we wskazanej warstwie
    def renameColums(self, layerName, oldColumnName, newColumnName):

        # Declare layer by name
        layer = QgsProject.instance().mapLayersByName(layerName)[0]
        # Start editing
        layer.startEditing()
        # Rename field
        for field in layer.fields():
            if field.name() == oldColumnName:
                idx = layer.fields().indexFromName(field.name())
                layer.renameAttribute(idx, newColumnName)

        # Close editing session and save changes
        layer.commitChanges()



    # Metoda zmieniająca nazwę kolumny we wskazanej warstwie
    def renameColumsByLayerInstance(self, layer, oldColumnName, newColumnName):

        # Start editing
        layer.startEditing()
        # Rename field
        for field in layer.fields():
            if field.name() == oldColumnName:
                idx = layer.fields().indexFromName(field.name())
                layer.renameAttribute(idx, newColumnName)

        # Close editing session and save changes
        layer.commitChanges()


    # Metoda przełączania checkbox
    def checkBoxSwitch(self, checkBox1, checkBox2):
        if checkBox1.isChecked():
            checkBox2.setChecked(False)




    # Metoda dodająca nową kolumnę
    def addNewColumnToLayerByLayerName(self, layerName, columnName, dataType):
        layer = QgsProject.instance().mapLayersByName(layerName)[0]
        layer_provider = layer.dataProvider()
        field_index = layer.fields().indexFromName(columnName)
        if field_index == -1:
            layer_provider.addAttributes([QgsField(columnName, dataType)])
        try:
            layer.updateFields()
        except:
            CustomMessageBox.showWithTimeout(5, "Nie dodano nowych kolumn! Sprawdź tabelę atrybutów", "", icon=QMessageBox.Warning)
        layer.commitChanges()
        layer.updateExtents()



    # Metoda dodająca nową kolumnę
    def addNewColumnToLayerByLayerInstance(self, layer, columnName, dataType):
        layer.startEditing()
        layer_provider = layer.dataProvider()
        field_index = layer.fields().indexFromName(columnName)
        if field_index == -1:
            layer_provider.addAttributes([QgsField(columnName, dataType)])
        try:
            layer.updateFields()
        except:
            CustomMessageBox.showWithTimeout(5, "Nie dodano nowych kolumn! Sprawdź tabelę atrybutów", "", icon=QMessageBox.Warning)
        layer.commitChanges()
        layer.updateExtents()




    # Metoda usuwająca  kolumnę
    def removeColumnToLayerByLayerInstance(self, layer, columnName):
        layer.startEditing()
        layer_provider = layer.dataProvider()
        field_index = layer.fields().indexFromName(columnName)
        if  field_index > -1:
            layer_provider.deleteAttributes([field_index])
        try:
            layer.updateFields()
        except:
            CustomMessageBox.showWithTimeout(5, "Nie usunięto kolum! Sprawdź tabelę atrybutów", "",
                                             icon=QMessageBox.Warning)
        layer.commitChanges()
        layer.updateExtents()




    # Metoda usuwająca  kolumny poza zadeklarowanmi
    def removeEachColumnExeptDeclaredByLayerInstance(self, layer, columns_to_leave):

        column_names = [field.name() for field in layer.fields()]
        reduced_column_names = [item for item in column_names if item not in columns_to_leave]

        layer.startEditing()
        layer_provider = layer.dataProvider()

        for column in reduced_column_names:

            field_index = layer.fields().indexFromName(column)
            if  field_index > -1:
                layer_provider.deleteAttributes([field_index])
            try:
                layer.updateFields()
            except:
                CustomMessageBox.showWithTimeout(5, "Nie usunięto kolumn! Sprawdź tabelę atrybutów", "", icon=QMessageBox.Warning)

        layer.commitChanges()
        layer.updateExtents()



    # Round data from column
    def roundDataInColumnByLayerInstance(self, layer, columnName, roundValue):
        layer_provider = layer.dataProvider()
        fieldToRound = layer.fields().indexFromName(columnName)
        for f in layer.getFeatures():
            id = f.id()
            feature = layer.getFeature(id)
            value = feature[fieldToRound] or 0
            newValue = round(value, roundValue)
            if newValue:
                attrNewValue = {fieldToRound: newValue}
            else:
                attrNewValue = {fieldToRound: value}
            layer_provider.changeAttributeValues({id: attrNewValue})
        try:
            layer.commitChanges()
        except:
            CustomMessageBox.showWithTimeout(5, "Proces zaokrąglania zakończył się niepowodzeniem!", "",icon=QMessageBox.Warning)


    # Recalculate ID
    def recalculateIDInColumnByLayerInstance(self, layer, columnName, initId):
        layer.startEditing()
        idx = layer.fields().indexFromName(columnName)
        for f in layer.getFeatures():
            f.setAttribute(idx, initId)
            layer.updateFeature(f)
            initId += 1
        try:
            layer.commitChanges()
        except:
            CustomMessageBox.showWithTimeout(5, "Proces przeliczania ID zakończył się niepowodzeniem!", "",
                                             icon=QMessageBox.Warning)

    # Metoda wymuszająca zapis zmian
    def forceStoEditing(self, layerName):
        layer = QgsProject.instance().mapLayersByName(layerName)[0]
        layer.commitChanges()
        layer.updateExtents()

    # Metoda sprawdzająca istnienie warstwy
    @staticmethod
    def layerByNameExists(layerName):
        return len(QgsProject.instance().mapLayersByName(layerName)) > 0

    # Metoda sprawdzająca istnienie kolumny we wskazanej warstwie
    @staticmethod
    def columnInLayerByNameExists(layerName, columnName):
        return AtributeTableManager.layerByNameExists(layerName) and \
               QgsProject.instance().mapLayersByName(layerName)[0].fields().indexFromName(columnName) > -1


    # Metoda wpisująca jednakową wartość w całej kolumnie wskazanej warstwy
    def fillWholeColumnInLayerWith(self, layerName, columnName, value):
        # poniższe przypadki w przyszłości można zastąpić wyrzucaniem wyjątków (tymczasowo można zakomentować)
        # gdy brak wartości
        if value is None:
            CustomMessageBox.showWithTimeout(5, "Wypełnianie wartości w kolumnie: brak wartości", "",
                                             icon=QMessageBox.Warning)
            return
        # gdy brak warstwy
        if not AtributeTableManager.layerByNameExists(layerName):
            CustomMessageBox.showWithTimeout(5, "Wypełnianie wartości w kolumnie: brak warstwy", "",
                                             icon=QMessageBox.Warning)
            return
        # gdy brak kolumny
        if not AtributeTableManager.columnInLayerByNameExists(layerName, columnName):
            CustomMessageBox.showWithTimeout(5, "Wypełnianie wartości w kolumnie: brak kolumny w warstwie", "",
                                             icon=QMessageBox.Warning)
            return


        layer = QgsProject.instance().mapLayersByName(layerName)[0]
        layer.startEditing()
        layer_provider = layer.dataProvider()

        field = layer.fields().indexFromName(columnName)
        attr_to = {field: value}

        for features in layer.getFeatures():
            id = features.id()
            layer_provider.changeAttributeValues({id: attr_to})

        layer.commitChanges()

    def setValueforFeatureColumnInLayer(self, layerName, columnName, featureDictQuery, value):
        """Add a toolbar icon to the toolbar.

        :param layerName: nazwa warstwy
        :type layerName: str

        :param columnName: nazwa kolumny
        :type columnName: str

        :param featureDictQuery: wskazuje obiekt do zmiany przez słownik - key (kolumna), value(wartość w kolumnie)
        :type featureDictQuery: dict

        :param value: wartość przypisywana do pola obiektu

        """

        # poniższe przypadki w przyszłości można zastąpić wyrzucaniem wyjątków (tymczasowo można zakomentować)
        # gdy brak wartości
        if value is None:
            # CustomMessageBox.showWithTimeout(5, "Zmiana wartości atrubutu: brak wartości", "", icon=QMessageBox.Warning)
            return
        # gdy brak warstwy
        if not AtributeTableManager.layerByNameExists(layerName):
            CustomMessageBox.showWithTimeout(5, "Zmiana wartości atrubutu: brak warstwy", "",
                                             icon=QMessageBox.Warning)
            return
        # gdy brak kolumny
        if not AtributeTableManager.columnInLayerByNameExists(layerName, columnName):
            CustomMessageBox.showWithTimeout(5, "Zmiana wartości atrubutu: brak kolumny w warstwie", "",
                                             icon=QMessageBox.Warning)
            return

        if featureDictQuery is None or not isinstance(featureDictQuery, dict):
            CustomMessageBox.showWithTimeout(5, "Zmiana wartości atrubutu: potrzeba słownika zapytania", "",
                                             icon=QMessageBox.Warning)
            return



        layer = QgsProject.instance().mapLayersByName(layerName)[0]
        layer.startEditing()
        layer_provider = layer.dataProvider()

        field = layer.fields().indexFromName(columnName)
        attr_to = {field: value}
        query = ' "{key}" = \'{value}\' '.format(**featureDictQuery)
        features_to_modify = layer.getFeatures(QgsFeatureRequest().setFilterExpression(query))

        for feature in features_to_modify:
            id = feature.id()
            layer_provider.changeAttributeValues({id: attr_to})

        layer.commitChanges()
