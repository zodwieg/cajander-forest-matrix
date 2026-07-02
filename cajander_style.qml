<!DOCTYPE qgis PUBLIC 'http://mrcc.com' 'SYSTEM'>
<qgis version="3.44.11-Solothurn" styleCategories="Symbology|Rendering">
  <pipe>
    <provider>
      <resampling enabled="false" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer type="paletted" band="1" opacity="0.5" nodataColor="">
      <colorPalette>
        <!-- === ЛОВУШКИ ДЛЯ ВСЕХ 30 ОШИБОЧНЫХ КОДОВ МАТРИЦЫ (ЧЕРНЫЙ ЦВЕТ) === -->
        <paletteEntry label="Ошибка 101" value="101" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 102" value="102" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 103" value="103" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 110" value="110" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 113" value="113" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 120" value="120" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 123" value="123" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 201" value="201" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 202" value="202" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 203" value="203" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 210" value="210" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 211" value="211" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 213" value="213" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 220" value="220" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 301" value="301" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 302" value="302" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 303" value="303" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 310" value="310" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 311" value="311" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 313" value="313" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 320" value="320" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 401" value="401" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 402" value="402" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 403" value="403" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 410" value="410" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 412" value="412" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 413" value="413" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 420" value="420" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 421" value="421" alpha="255" color="#000000"/>
        <paletteEntry label="Ошибка 422" value="422" alpha="255" color="#000000"/>

        <!-- === ВАЛИДНЫЕ КЛАССЫ === -->
        <!-- 1xx: Сухие -->
        <paletteEntry label="100 — Сухой луг / Вырубка / Пески" value="100" alpha="255" color="#F3E1B6"/>
        <paletteEntry label="111 — Сухое сосновое редколесье" value="111" alpha="255" color="#EED07E"/>
        <paletteEntry label="112 — Сухой молодой сосново-березовый лес" value="112" alpha="255" color="#EED07E"/>
        <paletteEntry label="121 — Сухой брусничный сосняк" value="121" alpha="255" color="#E5B842"/>
        <paletteEntry label="122 — Суховатый смешанный сосновый лес" value="122" alpha="255" color="#E5B842"/>

        <!-- 2xx: Свежие -->
        <paletteEntry label="200 — Свежий луг / Зарастающая пашня" value="200" alpha="255" color="#D1EAD4"/>
        <paletteEntry label="212 — Смешанный молодняк" value="212" alpha="255" color="#99D594"/>
        <paletteEntry label="221 — Свежий ельник черничный" value="221" alpha="255" color="#45A538"/>
        <paletteEntry label="222 — Свежий чернично-смешанный елово-березовый" value="222" alpha="255" color="#45A538"/>
        <paletteEntry label="223 — Свежий мелколиственный лес / Березняк" value="223" alpha="255" color="#45A538"/>

        <!-- 3xx: Влажные -->
        <paletteEntry label="300 — Влажный луг / Крупноосоковое безлесье" value="300" alpha="255" color="#C5E0DC"/>
        <paletteEntry label="312 — Влажный смешанный молодняк" value="312" alpha="255" color="#7CB3AC"/>
        <paletteEntry label="321 — Влажный долгомошный или кисличный ельник" value="321" alpha="255" color="#2A7E74"/>
        <paletteEntry label="322 — Влажные смешанные дебри вдоль ручьев" value="322" alpha="255" color="#2A7E74"/>
        <paletteEntry label="323 — Влажный пойменный ольшаник / Березняк" value="323" alpha="255" color="#2A7E74"/>

        <!-- 4xx: Болота -->
        <paletteEntry label="400 — Открытое сфагновое болота / Топь" value="400" alpha="255" color="#D0D9E9"/>
        <paletteEntry label="411 — Чахлый болотный сосняк на сфагнуме" value="411" alpha="255" color="#8AA2CE"/>
        <paletteEntry label="423 — Заболоченный ельник / Черноольховое болото" value="423" alpha="255" color="#3B5998"/>
      </colorPalette>
    </rasterrenderer>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
