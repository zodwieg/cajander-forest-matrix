<!DOCTYPE qgis PUBLIC 'http://mrcc.com' 'SYSTEM'>
<qgis version="3.28.0" styleCategories="Symbology|Visibility">
  <renderer-v2 type="RuleBasedRenderer" forceraster="0" symbollevels="0">
    <rules key="root">
      <rule filterExpression="&quot;forest_code&quot; % 10 = 1" label="Хвойные (•)" symbol="0"/>
      <rule filterExpression="&quot;forest_code&quot; % 10 = 2" label="Смешанные (x)" symbol="1"/>
      <rule filterExpression="&quot;forest_code&quot; % 10 = 3" label="Лиственные (|)" symbol="2"/>
    </rules>
    <symbols>
      <symbol type="marker" name="0" alpha="1">
        <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
          <prop k="name" v="circle"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="size" v="2.5"/>
        </layer>
      </symbol>
      <symbol type="marker" name="1" alpha="1">
        <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
          <prop k="name" v="cross"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="size" v="3.5"/>
        </layer>
      </symbol>
      <symbol type="marker" name="2" alpha="1">
        <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
          <prop k="name" v="line"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="size" v="3.5"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <layerGeometryType>0</layerGeometryType>
  <hasScaleBasedVisibilityFactor>1</hasScaleBasedVisibilityFactor>
  <minimumScale>5000</minimumScale>
  <maximumScale>0</maximumScale>
</qgis>
