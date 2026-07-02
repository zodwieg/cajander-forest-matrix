<!DOCTYPE qgis PUBLIC 'http://mrcc.com' 'SYSTEM'>
<qgis version="3.28.0" styleCategories="Symbology|Visibility">
  <renderer-v2 type="RuleBasedRenderer" forceraster="0" symbollevels="0">
    <rules key="root">
      <!-- Хвойные -->
      <rule label="Хвойные (•)" key="conifer">
        <symbol type="fill" name="sym_conifer" alpha="1">
          <!-- Делаем базовую заливку полигона абсолютно прозрачной -->
          <layer class="SimpleFill" locked="0" pass="0" enabled="1">
            <prop k="color" v="0,0,0,0"/>
            <prop k="outline_color" v="0,0,0,0"/>
          </layer>
          <!-- Генератор геометрии поверх прозрачного фона -->
          <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
            <prop k="SymbolType" v="Marker"/>
            <prop k="geometryModifier" v="collect_geometries(array_filter(geometries_to_array(centroids(grid(boundary(coalesce(intersection($geometry, @map_extent), $geometry)), 9.999818, 9.998777))), raster_value('________________________________b555ced9_1625_45a9_8d6e_9e00d1391dbe', 1, @element) % 10 = 1))"/>
            <symbol type="marker" name="inner_marker" alpha="1">
              <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
                <prop k="name" v="circle"/>
                <prop k="color" v="255,255,255,255"/>
                <prop k="outline_color" v="0,0,0,255"/>
                <prop k="outline_width" v="0.6"/>
                <prop k="size" v="2.5"/>
              </layer>
            </symbol>
          </layer>
        </symbol>
      </rule>
      <!-- Смешанные -->
      <rule label="Смешанные (x)" key="mixed">
        <symbol type="fill" name="sym_mixed" alpha="1">
          <layer class="SimpleFill" locked="0" pass="0" enabled="1">
            <prop k="color" v="0,0,0,0"/>
            <prop k="outline_color" v="0,0,0,0"/>
          </layer>
          <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
            <prop k="SymbolType" v="Marker"/>
            <prop k="geometryModifier" v="collect_geometries(array_filter(geometries_to_array(centroids(grid(boundary(coalesce(intersection($geometry, @map_extent), $geometry)), 9.999818, 9.998777))), raster_value('________________________________b555ced9_1625_45a9_8d6e_9e00d1391dbe', 1, @element) % 10 = 2))"/>
            <symbol type="marker" name="inner_marker" alpha="1">
              <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
                <prop k="name" v="cross"/>
                <prop k="color" v="255,255,255,255"/>
                <prop k="outline_color" v="0,0,0,255"/>
                <prop k="outline_width" v="0.6"/>
                <prop k="size" v="3.5"/>
              </layer>
            </symbol>
          </layer>
        </symbol>
      </rule>
      <!-- Лиственные -->
      <rule label="Лиственные (|)" key="deciduous">
        <symbol type="fill" name="sym_deciduous" alpha="1">
          <layer class="SimpleFill" locked="0" pass="0" enabled="1">
            <prop k="color" v="0,0,0,0"/>
            <prop k="outline_color" v="0,0,0,0"/>
          </layer>
          <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
            <prop k="SymbolType" v="Marker"/>
            <prop k="geometryModifier" v="collect_geometries(array_filter(geometries_to_array(centroids(grid(boundary(coalesce(intersection($geometry, @map_extent), $geometry)), 9.999818, 9.998777))), raster_value('________________________________b555ced9_1625_45a9_8d6e_9e00d1391dbe', 1, @element) % 10 = 3))"/>
            <symbol type="marker" name="inner_marker" alpha="1">
              <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
                <prop k="name" v="line"/>
                <prop k="color" v="255,255,255,255"/>
                <prop k="outline_color" v="0,0,0,255"/>
                <prop k="outline_width" v="0.6"/>
                <prop k="size" v="3.5"/>
              </layer>
            </symbol>
          </layer>
        </symbol>
      </rule>
    </rules>
  </renderer-v2>
  <layerGeometryType>2</layerGeometryType>
  <hasScaleBasedVisibilityFactor>1</hasScaleBasedVisibilityFactor>
  <minimumScale>5000</minimumScale>
  <maximumScale>0</maximumScale>
</qgis>
