#!/usr/bin/env python3
"""
Generate all PDP pages and download images from the live Wiewel Goudsmeden WordPress site.
Also rebuilds collectie.html to match the live site's product catalog.
"""
import os, urllib.request, json, re, html

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, 'assets', 'images', 'collectie')
COLLECTIE_DIR = os.path.join(BASE, 'collectie')

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(COLLECTIE_DIR, exist_ok=True)

# ============================================================
# PRODUCT DATA (from live site wiewelgoudsmeden.nl)
# ============================================================

PRODUCTS = [
    # === RINGEN ===
    {"slug": "alliance-roze-spinellen", "name": "Alliance met ovale roze spinellen", "category": "Ringen", "material": "Rosé goud 18kt, spinel", "metal": "18 karaat rosé goud", "stone": "Ovale roze spinellen", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/91-DSC_5765-End-480x480.jpg", "desc": "Een verfijnde alliance ring bezet met ovale roze spinellen in warm rosé goud. De zachte kleur van de spinellen harmonieert prachtig met het rosé goud, wat een vrouwelijk en eigentijds sieraad oplevert.", "request": False},
    {"slug": "cacholong-opaal-aquamarijn-ring", "name": "Cacholong opaal en aquamarijn ring", "category": "Ringen", "material": "Rosé goud 18kt, cacholong opaal, aquamarijn", "metal": "18 karaat rosé goud", "stone": "Cacholong opaal", "accent": "Aquamarijn", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3696-480x480.jpg", "desc": "Een opvallende ring waarin melkwitte cacholong opaal en heldere aquamarijn samenkomen. Het contrast tussen de stenen geeft dit stuk een serene, maar tegelijk markante uitstraling.", "request": False},
    {"slug": "gele-diamant-ring", "name": "Gele diamant ring", "category": "Ringen", "material": "Geel goud 18kt, diamant", "metal": "18 karaat geelgoud", "stone": "Gele diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3422-480x480.jpg", "desc": "Een bijzondere ring met een warm gekleurde gele diamant als middelpunt. De gele diamant is zeldzaam en geeft deze ring een exclusief karakter.", "request": False},
    {"slug": "maansteen-saffieren-ring", "name": "Maansteen en saffieren ring", "category": "Ringen", "material": "Rosé goud 18kt, maansteen, saffier", "metal": "18 karaat rosé goud", "stone": "Maansteen", "accent": "Saffier", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_9308-480x480.jpg", "desc": "De mysterieuze glans van maansteen gecombineerd met de diepe kleur van saffier. Een ring die speelt met licht en het oog vangt bij elke beweging.", "request": False},
    {"slug": "platina-ring-groene-saffier", "name": "Platina ring met groene saffier", "category": "Ringen", "material": "Platina, saffier", "metal": "Platina", "stone": "Groene saffier", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/164-DSC_7200-End-480x480.jpg", "desc": "Een stoere herenring in platina met een levendige groene saffier. De robuuste band en warme kleur van de steen maken dit tot een uniek herensieraad.", "request": False},
    {"slug": "ring-rutielkwarts-diamant", "name": "Ring met rutielkwarts en diamant", "category": "Ringen", "material": "Geel goud 18kt, rutielkwarts, diamant", "metal": "18 karaat geelgoud", "stone": "Rutielkwarts", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3738-480x480.jpg", "desc": "Rutielkwarts met zijn kenmerkende gouden naaldinsluitsels maakt elke steen uniek. Geflankeerd door diamanten in een warme geelgouden zetting.", "request": False},
    {"slug": "witgouden-alliance-diamant", "name": "Witgouden alliance met diamant", "category": "Ringen", "material": "Wit goud 18kt, diamant", "metal": "18 karaat witgoud", "stone": "Briljant geslepen diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3418-480x480.jpg", "desc": "Een tijdloze alliance ring in witgoud, bezet met schitterende briljant geslepen diamanten. Ideaal als trouwring of als elegant dagelijks sieraad.", "request": False},
    {"slug": "alliance-briljant-diamant", "name": "Alliance ring met diamanten", "category": "Ringen", "material": "Platina, diamant", "metal": "Platina", "stone": "Briljant geslepen diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/alliance-briljant-x1-480x480.jpg", "desc": "Een klassieke alliance in platina, rondom bezet met briljant geslepen diamanten. Platina garandeert een levenslang behoud van glans en stevigheid.", "request": False},
    {"slug": "alliance-platina-asscher", "name": "Platina ring met Asscher geslepen diamanten", "category": "Ringen", "material": "Platina, diamant", "metal": "Platina", "stone": "Asscher geslepen diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/45-DSC_5110-End-480x480.jpg", "desc": "De Asscher slijpvorm, vernoemd naar de Amsterdamse diamantslijper Joseph Asscher, geeft deze platina ring een art deco uitstraling met een moderne twist.", "request": False},
    {"slug": "platina-alliance-princess", "name": "Platina ring met princess geslepen diamanten", "category": "Ringen", "material": "Platina, diamant", "metal": "Platina", "stone": "Princess geslepen diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/46-DSC_5117-End-480x480.jpg", "desc": "Princess geslepen diamanten in een strakke platina band. De vierkante slijpvorm geeft een modern en grafisch effect dat opvalt door zijn scherpte.", "request": False},
    {"slug": "geelgouden-aanschuifring", "name": "Geelgouden aanschuifring", "category": "Ringen", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/06-DSC_2532-End-480x480.jpg", "desc": "Een minimalistische aanschuifring in warm geelgoud. Perfect om te combineren met andere ringen of als subtiel solitair statement.", "request": False},
    {"slug": "ring-zuidzeeparel-groene-diamant", "name": "Ring met Zuidzee parel en groene diamant", "category": "Ringen", "material": "Geel goud 18kt, diamant, Zuidzee parel", "metal": "18 karaat geelgoud", "stone": "Gouden Zuidzee parel", "accent": "Groene diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/03-DSC_4734-End-480x480.jpg", "desc": "Een unieke combinatie van een gouden Zuidzee parel en een zeldzame groene diamant. Twee bijzondere stenen die elkaar in deze ring versterken.", "request": False},
    {"slug": "ring-tahiti-parel", "name": "Ring met Tahiti parel", "category": "Ringen", "material": "Geel goud 18kt, Tahiti parel", "metal": "18 karaat geelgoud", "stone": "Tahiti parel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/05-DSC_4752-End-480x480.jpg", "desc": "Een ring met de kenmerkende donkere glans van een Tahiti parel. De warme geelgouden band laat de parel alle aandacht trekken.", "request": False},
    {"slug": "ring-zuidzeeparel", "name": "Ring met Zuidzee parel", "category": "Ringen", "material": "Geel goud 18kt, Zuidzee parel", "metal": "18 karaat geelgoud", "stone": "Zuidzee parel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/04-DSC_4744-End-480x480.jpg", "desc": "Een elegante ring met een lichtgekleurde Zuidzee parel. De zachte glans van de parel maakt dit tot een verfijnd en draagbaar sieraad.", "request": False},
    {"slug": "peridot-diamanten-ring", "name": "Peridot en diamanten ring", "category": "Ringen", "material": "Geel goud 18kt, diamant, peridoot", "metal": "18 karaat geelgoud", "stone": "Peridoot", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/02-DSC_2639-End-480x480.jpg", "desc": "De levendige olijfgroene kleur van peridoot gecombineerd met het vuur van diamanten. Een ring die opvalt door zijn frisheid en kleur.", "request": False},
    {"slug": "platina-ring-blauwe-saffier", "name": "Platina ring met blauwe saffier", "category": "Ringen", "material": "Platina, saffier, diamant", "metal": "Platina", "stone": "Blauwe saffier", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/50-DSC_5162-End-480x480.jpg", "desc": "Een klassieke combinatie van diepblauwe saffier en diamant in platina. De koninklijke kleur van saffier maakt dit tot een tijdloos stuk.", "request": False},
    {"slug": "platina-ring-bruine-diamant", "name": "Platina ring met bruine diamant", "category": "Ringen", "material": "Platina, bruine diamant, diamant", "metal": "Platina", "stone": "Bruine diamant", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/23-DSC_3243-End-480x480.jpg", "desc": "Een warme bruine diamant als middelpunt, geflankeerd door heldere diamanten in platina. Het contrast tussen warm en koel geeft deze ring karakter.", "request": False},
    {"slug": "ring-groene-toermalijn", "name": "Ring groene toermalijn", "category": "Ringen", "material": "Geel goud 18kt, toermalijn", "metal": "18 karaat geelgoud", "stone": "Groene toermalijn", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/01-DSC_2621-End-480x480.jpg", "desc": "Een geelgouden ring met een levendige groene toermalijn als centrale steen. De intense kleur van de toermalijn maakt elk exemplaar uniek.", "request": False},
    {"slug": "ring-paarse-jade", "name": "Ring met paarse jade", "category": "Ringen", "material": "Geel goud 18kt, jade, diamant", "metal": "18 karaat geelgoud", "stone": "Paarse jade", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3729-480x480.jpg", "desc": "Paarse jade is uitzonderlijk zeldzaam. In combinatie met diamant en warm geelgoud ontstaat een ring die zowel mysterieus als elegant is.", "request": False},
    {"slug": "ring-rubeliet-diamant", "name": "Ring met rubeliet en diamant", "category": "Ringen", "material": "Rosé goud 18kt, rubeliet, diamant", "metal": "18 karaat rosé goud", "stone": "Rubeliet", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/44-DSC_5097-End-480x480.jpg", "desc": "Rubeliet, de roze variëteit van toermalijn, schittert in deze rosé gouden ring. Diamanten accentueren de warme gloed van de centrale steen.", "request": False},
    {"slug": "ring-turkoois", "name": "Ring met turkoois", "category": "Ringen", "material": "Geel goud 18kt, turkoois", "metal": "18 karaat geelgoud", "stone": "Turkoois", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_5210-End-480x480.jpg", "desc": "De karakteristieke hemelsblauwe kleur van turkoois in een warm geelgouden zetting. Een sieraad met een vleugje bohemian elegantie.", "request": False},
    {"slug": "ring-toermalijnkwarts", "name": "Ring toermalijnkwarts", "category": "Ringen", "material": "Rood goud 18kt, toermalijnkwarts, diamant", "metal": "18 karaat rood goud", "stone": "Toermalijnkwarts", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/ring-toermalijnkwarts-x11-480x480.jpg", "desc": "Toermalijnkwarts bevat naaldvormige insluitsels van toermalijn die elke steen een uniek patroon geven. In rood goud met diamantaccenten.", "request": False},
    {"slug": "ring-mandarijngranaat", "name": "Roségouden ring met mandarijngranaat", "category": "Ringen", "material": "Rosé goud 18kt, mandarijn granaat", "metal": "18 karaat rosé goud", "stone": "Mandarijngranaat", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/18-DSC_2583-End-480x480.jpg", "desc": "De warme oranje gloed van mandarijngranaat in rosé goud. Een zeldzame edelsteen die deze ring tot een bijzonder bezit maakt.", "request": False},

    # === OORBELLEN (selection of 33 — all included) ===
    {"slug": "bruine-diamant-koraal-oorbellen", "name": "Bruine diamant en koraal oorbellen", "category": "Oorbellen", "material": "Rosé goud 18kt, bruine diamant, koraal", "metal": "18 karaat rosé goud", "stone": "Bruine diamant", "accent": "Koraal", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3664-480x480.jpg", "desc": "Een opvallende combinatie van bruine diamant en warm koraal in rosé goud. De aardse tinten geven deze oorbellen een organische elegantie.", "request": False},
    {"slug": "creolen-amethist-trosjes", "name": "Creolen met amethist trosjes", "category": "Oorbellen", "material": "Wit goud 18kt, amethist", "metal": "18 karaat witgoud", "stone": "Amethist", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3499-480x480.jpg", "desc": "Witgouden creolen met speelse trosjes amethist die bewegen bij elke stap. De paarse tinten van amethist geven een koninklijke uitstraling.", "request": False},
    {"slug": "creolen-spinel-trosjes", "name": "Creolen met spinel trosjes", "category": "Oorbellen", "material": "Rosé goud 18kt, spinel", "metal": "18 karaat rosé goud", "stone": "Spinel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3486-480x480.jpg", "desc": "Rosé gouden creolen met trosjes roze spinel die een vrouwelijke en levendige uitstraling geven. Licht en comfortabel om te dragen.", "request": False},
    {"slug": "creolen-tanzaniet-trosjes", "name": "Creolen met tanzaniet trosjes", "category": "Oorbellen", "material": "Wit goud 18kt, tanzaniet", "metal": "18 karaat witgoud", "stone": "Tanzaniet", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3503-480x480.jpg", "desc": "Witgouden creolen met trosjes van diepblauwe tanzaniet. Tanzaniet komt alleen voor in Tanzania en is duizend keer zeldzamer dan diamant.", "request": False},
    {"slug": "diamant-zoetwaterparel-oorhaken", "name": "Diamant en zoetwaterparel oorhaken", "category": "Oorbellen", "material": "Geel goud 18kt, zoetwaterparel, diamant", "metal": "18 karaat geelgoud", "stone": "Zoetwaterparel", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3635-480x480.jpg", "desc": "Elegante oorhaken met de zachte glans van zoetwaterparels, geaccentueerd door diamanten. Een tijdloze combinatie in warm geelgoud.", "request": False},
    {"slug": "diamanten-tweezijdige-creolen", "name": "Diamanten tweezijdige creolen", "category": "Oorbellen", "material": "Geel goud en wit goud 18kt, diamant", "metal": "18 karaat geel- en witgoud", "stone": "Diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3626-480x480.jpg", "desc": "Unieke tweezijdige creolen met diamanten aan beide zijden. De combinatie van geel- en witgoud geeft extra dimensie en speelsheid.", "request": False},
    {"slug": "gouden-zuidzee-pareloorbellen", "name": "Gouden Zuidzee pareloorbellen", "category": "Oorbellen", "material": "Geel goud 18kt, Zuidzee parel", "metal": "18 karaat geelgoud", "stone": "Zuidzee parel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_6328-End-480x480.jpg", "desc": "Lichtgekleurde Zuidzee parels met een warm gouden glans. Elke parel is uniek in vorm en kleur, wat deze oorbellen bijzonder maakt.", "request": False},
    {"slug": "oorclips-amethist-zoetwaterparel", "name": "Oorclips met amethist en zoetwaterparel", "category": "Oorbellen", "material": "Wit goud 18kt, amethist, parel", "metal": "18 karaat witgoud", "stone": "Amethist", "accent": "Zoetwaterparel", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC2972-480x480.jpg", "desc": "Oorclips zonder gaatjes, met amethist en zoetwaterparel in witgoud. Comfortabel te dragen en geschikt voor elke gelegenheid.", "request": False},
    {"slug": "oorhaken-amethist", "name": "Oorhaken amethist", "category": "Oorbellen", "material": "Rosé goud 18kt, amethist", "metal": "18 karaat rosé goud", "stone": "Amethist", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/91-DSC_6706-End-480x480.jpg", "desc": "Sierlijke oorhaken met amethist in warm rosé goud. De diepe paarse kleur van de amethist contrasteert mooi met het zachte rosé.", "request": False},
    {"slug": "oorhaken-turkoois", "name": "Oorhaken met turkoois", "category": "Oorbellen", "material": "Geel goud 18kt, turkoois", "metal": "18 karaat geelgoud", "stone": "Turkoois", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_9442-480x480.jpg", "desc": "Hemelsblauwe turkoois aan geelgouden oorhaken. De levendige kleur van turkoois maakt deze oorbellen tot een opvallend accessoire.", "request": False},
    {"slug": "oorhangers-witte-zoetwaterparel", "name": "Oorhangers met witte zoetwaterparel", "category": "Oorbellen", "material": "Geel goud 18kt, zoetwaterparel", "metal": "18 karaat geelgoud", "stone": "Witte zoetwaterparel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_9705-480x480.jpg", "desc": "Sierlijke oorhangers met witte zoetwaterparels. De zachte luster van de parels geeft een verfijnde en klassieke uitstraling.", "request": False},
    {"slug": "roze-maansteen-diamanten-oorhaken", "name": "Roze maansteen met diamanten oorhaken", "category": "Oorbellen", "material": "Geel goud 18kt, maansteen, diamant", "metal": "18 karaat geelgoud", "stone": "Roze maansteen", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3606-480x480.jpg", "desc": "Roze maansteen met haar kenmerkende adularescentie, geaccentueerd door diamanten. Een etherisch sieraad dat licht lijkt te vangen.", "request": False},
    # Page 2
    {"slug": "solitair-oorstekers-triangel-diamant", "name": "Solitair oorstekers triangel geslepen diamant", "category": "Oorbellen", "material": "Wit goud 18kt, diamant", "metal": "18 karaat witgoud", "stone": "Triangel geslepen diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_6157-End-480x480.jpg", "desc": "Oorstekers met een bijzondere triangel (driehoek) slijpvorm. Een moderne interpretatie van de klassieke diamant oorstuds.", "request": False},
    {"slug": "witgouden-agaat-oorhaken", "name": "Witgouden agaat oorhaken", "category": "Oorbellen", "material": "Wit goud 18kt, agaat", "metal": "18 karaat witgoud", "stone": "Agaat", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_9434-480x480.jpg", "desc": "Oorhaken met agaat in witgoud. De aardse tinten en natuurlijke patronen van agaat maken elke steen tot een klein kunstwerk.", "request": False},
    {"slug": "witgouden-creolen", "name": "Witgouden creolen", "category": "Oorbellen", "material": "Wit goud 18kt", "metal": "18 karaat witgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3599-480x480.jpg", "desc": "Klassieke creolen in witgoud, volledig met de hand gesmeed. Het koele witgoud geeft een moderne en strakke uitstraling.", "request": False},
    {"slug": "witgouden-creolen-diamant", "name": "Witgouden creolen met diamant", "category": "Oorbellen", "material": "Wit goud 18kt, diamant", "metal": "18 karaat witgoud", "stone": "Diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/56-DSC_6063-End-480x480.jpg", "desc": "Witgouden creolen verrijkt met diamanten. De schittering van de diamanten geeft deze creolen extra allure.", "request": False},
    {"slug": "zuidzeeparel-citrien-pampels", "name": "Zuidzeeparel met afneembare citrien pampels", "category": "Oorbellen", "material": "Wit goud 18kt, Zuidzee parel, citrien", "metal": "18 karaat witgoud", "stone": "Zuidzee parel", "accent": "Citrien", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_7407-480x480.jpg", "desc": "Veelzijdige oorbellen: draag de Zuidzee parels alleen, of voeg de citrien pampels toe voor een uitbundiger effect. Twee sieraden in één.", "request": False},
    {"slug": "geelgouden-creolen", "name": "Geelgouden creolen", "category": "Oorbellen", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/19-DSC_4449-End-480x480.jpg", "desc": "Handgesmede creolen in warm geelgoud. De organische vorm en het warme materiaal maken deze creolen tot een tijdloos bezit.", "request": True},
    {"slug": "geelgouden-gladde-creolen", "name": "Geelgouden gladde creolen", "category": "Oorbellen", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/creolen-geel-AU-x11-480x480.jpg", "desc": "Soepele, gladde creolen in 18 karaat geelgoud. Minimalistisch ontwerp, maximale elegantie. Perfect voor dagelijks gebruik.", "request": False},
    {"slug": "grote-barnsteen-oorbellen", "name": "Grote barnsteen oorbellen", "category": "Oorbellen", "material": "Geel goud 18kt, barnsteen", "metal": "18 karaat geelgoud", "stone": "Barnsteen", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/20-DSC_4556-End-480x480.jpg", "desc": "Opvallende oorbellen met grote barnstenen in geelgoud. Barnsteen, miljoenen jaren oud fossiel hars, geeft elk stuk een warme gouden gloed.", "request": False},
    {"slug": "mammoet-ivoor-oorbellen", "name": "Mammoet ivoor oorbellen", "category": "Oorbellen", "material": "Geel goud 18kt, mammoet ivoor", "metal": "18 karaat geelgoud", "stone": "Mammoet ivoor", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/39-DSC_3833-End-480x480.jpg", "desc": "Oorbellen met ethisch verantwoord mammoet ivoor, duizenden jaren oud. Een bijzonder en duurzaam materiaal in combinatie met geelgoud.", "request": False},
    {"slug": "maud-geelgouden-creolen", "name": "Maud – Geelgouden creolen", "category": "Oorbellen", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/oorbellen-maud-geelgoud-x11-480x480.jpg", "desc": "De Maud creolen in geelgoud combineren een klassieke creool vorm met een eigentijdse afwerking. Een van onze populairste ontwerpen.", "request": False},
    {"slug": "maud-diamanten-creolen", "name": "Maud – Witgouden creolen diamant", "category": "Oorbellen", "material": "Wit goud 18kt, diamant", "metal": "18 karaat witgoud", "stone": "Diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/oorbellen-maud-diamant-x11-480x480.jpg", "desc": "De Maud creolen in witgoud, bezet met diamanten voor extra schittering. Elegant genoeg voor speciale gelegenheden, verfijnd genoeg voor elke dag.", "request": True},
    {"slug": "gestreepte-agaat-oorbellen", "name": "Oorbellen gestreepte agaat", "category": "Oorbellen", "material": "Wit goud 18kt, agaat", "metal": "18 karaat witgoud", "stone": "Gestreepte agaat", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/30-DSC_4023-End-480x480.jpg", "desc": "Witgouden oorbellen met gestreepte agaat. De natuurlijke strepen in de steen maken elk paar uniek.", "request": False},
    # Page 3
    {"slug": "lemon-chrysopraas-oorbellen", "name": "Oorbellen lemon chrysopraas", "category": "Oorbellen", "material": "Wit goud 18kt, lemon chrysopraas", "metal": "18 karaat witgoud", "stone": "Lemon chrysopraas", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/32-DSC_4093-End-480x480.jpg", "desc": "Frisgroene lemon chrysopraas in witgoud. De heldere kleur van deze zeldzame edelsteen brengt een zomerse elegantie.", "request": False},
    {"slug": "oorbellen-maansteen-blauwe-saffier", "name": "Oorbellen maansteen en blauwe saffier", "category": "Oorbellen", "material": "Wit goud 18kt, maansteen, saffier", "metal": "18 karaat witgoud", "stone": "Maansteen", "accent": "Blauwe saffier", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/26-DSC_4580-End-480x480.jpg", "desc": "De etherische glans van maansteen gecombineerd met de diepe kleur van blauwe saffier. Een betoverende combinatie in witgoud.", "request": False},
    {"slug": "oorbellen-maansteen-chalcedoon", "name": "Oorbellen maansteen en chalcedoon", "category": "Oorbellen", "material": "Wit goud 18kt, maansteen, chalcedoon", "metal": "18 karaat witgoud", "stone": "Maansteen", "accent": "Chalcedoon", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/23-DSC_4236-End-480x480.jpg", "desc": "Zachte tinten van maansteen en chalcedoon in witgoud. Een sieraad dat rust en elegantie uitstraalt.", "request": False},
    {"slug": "oorbellen-toermalijnkwarts", "name": "Oorbellen met toermalijnkwarts", "category": "Oorbellen", "material": "Wit goud 18kt, toermalijnkwarts", "metal": "18 karaat witgoud", "stone": "Toermalijnkwarts", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/18-DSC_4498-End-480x480.jpg", "desc": "Oorbellen met toermalijnkwarts, waarin zwarte toermalijn naaldinsluitsels een uniek patroon vormen in het heldere kwarts.", "request": False},
    {"slug": "oorclips-mammoet-ivoor-hout", "name": "Oorclips met mammoet ivoor en hout", "category": "Oorbellen", "material": "Geel goud 18kt, mammoet ivoor, hout", "metal": "18 karaat geelgoud", "stone": "Mammoet ivoor", "accent": "Hout", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/03-DSC_4479-End-480x480.jpg", "desc": "Oorclips die natuurlijke materialen combineren: prehistorisch mammoet ivoor en warm hout, in een geelgouden setting.", "request": False},
    {"slug": "solitair-oorstekers-diamant", "name": "Solitair oorstekers diamant", "category": "Oorbellen", "material": "Geel goud 18kt, diamant", "metal": "18 karaat geelgoud", "stone": "Diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/44-DSC_5142-End-480x480.jpg", "desc": "Tijdloze solitair oorstekers met briljant geslepen diamant in geelgoud. Het ultieme klassieke oorsieraad.", "request": False},
    {"slug": "robijn-oorstekers", "name": "Solitair oorstekers robijn", "category": "Oorbellen", "material": "Wit goud 18kt, robijn", "metal": "18 karaat witgoud", "stone": "Robijn", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/05-DSC_4411-End-480x480.jpg", "desc": "Oorstekers met diep rode robijn in witgoud. Robijn is na diamant de hardste edelsteen en staat symbool voor passie en liefde.", "request": False},
    {"slug": "tahiti-parel-oorbellen", "name": "Tahiti parel oorbellen", "category": "Oorbellen", "material": "Wit goud 18kt, Tahiti parel", "metal": "18 karaat witgoud", "stone": "Tahiti parel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/oorbellen-zwanenhals-grijze-parel-x11-480x480.jpg", "desc": "Elegante oorbellen met donkere Tahiti parels aan sierlijke witgouden zwanenhals haken. De parelmoer glans varieert van zilver tot aubergine.", "request": False},
    {"slug": "tweekleurige-tahitiparel-oorbellen", "name": "Tweekleurige Tahitiparel oorbellen", "category": "Oorbellen", "material": "Wit goud 18kt, Tahiti parel", "metal": "18 karaat witgoud", "stone": "Tweekleurige Tahiti parel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/12-DSC_4342-End-480x480.jpg", "desc": "Bijzondere Tahiti parels met een tweekleurig effect. Elke parel toont een uniek kleurenspel van donker naar licht.", "request": False},

    # === COLLIERS (selection — 21 total) ===
    {"slug": "collier-indigoliet-toermalijn", "name": "Collier Indigoliet toermalijn", "category": "Colliers", "material": "Geel goud 18kt, toermalijn", "metal": "18 karaat geelgoud", "stone": "Indigoliet toermalijn", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/40-DSC_5740-End-480x480.jpg", "desc": "Een prachtig collier van indigoliet toermalijn, een zeldzame blauwe variëteit. De stenen zijn individueel geselecteerd op kleur en helderheid.", "request": False},
    {"slug": "fijn-gele-saffier-collier", "name": "Fijn gele saffier collier", "category": "Colliers", "material": "Geel goud 18kt, saffier", "metal": "18 karaat geelgoud", "stone": "Gele saffier", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC2874-480x480.jpg", "desc": "Een fijn collier van gele saffierkralen met een geelgouden sluiting. De warme kleur van gele saffier geeft een zonnige uitstraling.", "request": False},
    {"slug": "fijn-multicolour-bruin-saffier-collier", "name": "Fijn multicolour bruin saffier collier", "category": "Colliers", "material": "Geel goud en wit goud 18kt, saffier", "metal": "18 karaat geel- en witgoud", "stone": "Bruine saffier", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC2906-480x480.jpg", "desc": "Een subtiel collier van bruine saffierkralen in warme aardetinten. De geel- en witgouden sluiting maakt het geheel compleet.", "request": False},
    {"slug": "fijn-multicolour-saffier-collier", "name": "Fijn multicolour saffier collier", "category": "Colliers", "material": "Wit goud 18kt, saffier", "metal": "18 karaat witgoud", "stone": "Multicolour saffier", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3675-480x480.jpg", "desc": "Een kleurrijk collier van saffieren in diverse tinten: van roze via oranje tot blauw. Elke steen is op kleur gesorteerd voor een harmonieus verloop.", "request": False},
    {"slug": "fijn-multicolour-toermalijn-collier", "name": "Fijn multicolour toermalijn collier", "category": "Colliers", "material": "Geel goud 18kt, toermalijn", "metal": "18 karaat geelgoud", "stone": "Multicolour toermalijn", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC2715-480x480.jpg", "desc": "Een levendig collier van toermalijn in alle kleuren van de regenboog. Toermalijn is de meest kleurrijke edelsteen die er bestaat.", "request": False},
    {"slug": "rubeliet-collier", "name": "Fijn rubeliet collier", "category": "Colliers", "material": "Geel goud 18kt, rubeliet", "metal": "18 karaat geelgoud", "stone": "Rubeliet", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/70-DSC_6495-End-480x480.jpg", "desc": "Een fijn collier van roze rubeliet kralen. Rubeliet is de roze tot rode variëteit van toermalijn met een intense, warme kleur.", "request": False},
    {"slug": "fijn-toermalijnsnoer-blauw", "name": "Fijn toermalijn collier blauw", "category": "Colliers", "material": "Geel goud 18kt, toermalijn", "metal": "18 karaat geelgoud", "stone": "Blauwe toermalijn", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/69-DSC_6494-End-480x480.jpg", "desc": "Een fijn collier van blauwe toermalijn kralen. De koele blauwe tinten variëren van hemelsblauw tot diep oceaanblauw.", "request": False},
    {"slug": "groen-barnsteen-collier", "name": "Groen barnsteen collier", "category": "Colliers", "material": "Geel goud 18kt, barnsteen", "metal": "18 karaat geelgoud", "stone": "Groene barnsteen", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_5823-End-480x480.jpg", "desc": "Een opvallend collier van zeldzame groene barnsteen. Groene barnsteen is bijzonder schaars en heeft een warme, organische uitstraling.", "request": False},
    {"slug": "lang-bloedkoraal-collier", "name": "Lang bloedkoraal collier", "category": "Colliers", "material": "Rosé goud en wit goud 18kt, bloedkoraal", "metal": "18 karaat rosé en witgoud", "stone": "Bloedkoraal", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/74-DSC_7222-End-480x480.jpg", "desc": "Een lang statement collier van diep rood bloedkoraal met rosé en witgouden accenten. Bloedkoraal staat symbool voor kracht en vitaliteit.", "request": False},
    {"slug": "multicolour-koraal-collier", "name": "Multicolour koraal collier", "category": "Colliers", "material": "Geel goud 18kt, koraal", "metal": "18 karaat geelgoud", "stone": "Koraal", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/80-DSC_8018-480x480.jpg", "desc": "Een kleurrijk collier van koraal in diverse tinten, van zachtroze tot diep oranje. De gouden sluiting maakt het geheel luxueus.", "request": False},
    {"slug": "roze-spinel-collier", "name": "Roze spinel collier", "category": "Colliers", "material": "Geel goud 18kt, spinel", "metal": "18 karaat geelgoud", "stone": "Roze spinel", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC2758-480x480.jpg", "desc": "Een verfijnd collier van roze spinel kralen met een geelgouden sluiting. Spinel is een van de meest onderschatte edelstenen.", "request": False},
    {"slug": "snoer-zwarte-spinel", "name": "Snoer van zwarte spinel", "category": "Colliers", "material": "Geel goud 18kt, spinel", "metal": "18 karaat geelgoud", "stone": "Zwarte spinel", "accent": None, "making": "Volledig met de hand geregen en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/79-DSC_7271-End-480x480.jpg", "desc": "Een stijlvol snoer van zwarte spinel met geelgouden sluiting. Het diepe zwart van spinel geeft een chique, veelzijdige uitstraling.", "request": False},
    # Page 2 colliers
    {"slug": "platina-collier-bruine-diamant", "name": "Platina collier met bruine diamant", "category": "Colliers", "material": "Platina, diamant", "metal": "Platina", "stone": "Bruine diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/12-DSC_3665-End-480x480.jpg", "desc": "Een verfijnd platina collier met een bruine diamant als hangertje. De warme tint van de diamant contrasteert mooi met het koele platina.", "request": False},
    {"slug": "mammoet-ebbenhout-collier", "name": "Mammoet ivoor en ebbenhout collier", "category": "Colliers", "material": "Wit goud 18kt, mammoet ivoor, hout", "metal": "18 karaat witgoud", "stone": "Mammoet ivoor", "accent": "Ebbenhout", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/27-DSC_5072-End-480x480.jpg", "desc": "Een uniek collier dat prehistorisch mammoet ivoor combineert met donker ebbenhout. Natuurlijke materialen in een witgouden afwerking.", "request": False},
    {"slug": "mammoet-collier", "name": "Mammoet ivoor collier", "category": "Colliers", "material": "Rosé goud 18kt, mammoet ivoor", "metal": "18 karaat rosé goud", "stone": "Mammoet ivoor", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/28-DSC_5070-End-480x480.jpg", "desc": "Een collier van mammoet ivoor schijven met rosé gouden verbindingen. Elk stuk ivoor is duizenden jaren oud en ethisch verantwoord.", "request": False},
    {"slug": "roze-zoetwater-parelsnoer", "name": "Snoer roze zoetwaterparels", "category": "Colliers", "material": "Geel goud 18kt, zoetwaterparel", "metal": "18 karaat geelgoud", "stone": "Roze zoetwaterparel", "accent": None, "making": "Met de hand geknoopt en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/06-DSC_3555-End-480x480.jpg", "desc": "Een romantisch snoer van roze zoetwaterparels met een geelgouden sluiting. De zachte roze glans is vrouwelijk en tijdloos.", "request": False},
    {"slug": "barok-tahiti-parel-collier", "name": "Collier Tahiti parels barok", "category": "Colliers", "material": "Geel goud en rosé goud 18kt, Tahiti parel", "metal": "18 karaat geel- en rosé goud", "stone": "Barok Tahiti parel", "accent": None, "making": "Met de hand geknoopt en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/04-DSC_3565-End-480x480.jpg", "desc": "Barok gevormde Tahiti parels met hun onregelmatige, natuurlijke vormen. Elke parel is uniek, wat dit collier tot een echt statement maakt.", "request": False},
    {"slug": "tahiti-parelsnoer-luxe-sluiting", "name": "Snoer Tahiti parels met diamanten sluiting", "category": "Colliers", "material": "Wit goud 18kt, diamant, Tahiti parel", "metal": "18 karaat witgoud", "stone": "Tahiti parel", "accent": "Diamant", "making": "Met de hand geknoopt en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/03-DSC_3639-End-480x480.jpg", "desc": "Een luxueus snoer van Tahiti parels met een handgesmede witgouden sluiting bezet met diamanten. Het ultieme parelsnoer.", "request": False},
    {"slug": "zoetwater-parelsnoer", "name": "Collier zoetwaterparels", "category": "Colliers", "material": "Wit goud 18kt, zoetwaterparel", "metal": "18 karaat witgoud", "stone": "Zoetwaterparel", "accent": None, "making": "Met de hand geknoopt en afgewerkt", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/07-DSC_3570-End-480x480.jpg", "desc": "Een klassiek parelsnoer van lichtgekleurde zoetwaterparels met een witgouden sluiting. Tijdloze elegantie voor elke gelegenheid.", "request": False},
    {"slug": "collier-ruwe-spinel", "name": "Grillig spinel collier", "category": "Colliers", "material": "Wit goud 18kt, spinel", "metal": "18 karaat witgoud", "stone": "Ruwe spinel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/22-DSC_3516-End-480x480.jpg", "desc": "Een expressief collier van grillig gevormde spinel stenen. De ruwe, ongepolijste vorm geeft dit stuk een organische en eigenzinnige uitstraling.", "request": False},
    {"slug": "zilveren-hanger-eikeltje", "name": "Zilveren hanger met amethist eikeltje", "category": "Colliers", "material": "Zilver en geel goud 18kt, amethist", "metal": "Zilver en 18 karaat geelgoud", "stone": "Amethist", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/collier-hanger-eikel-31-480x480.jpg", "desc": "Een speelse hanger in de vorm van een eikeltje, vervaardigd in zilver en geelgoud met een amethist. Een charmant en betaalbaar sieraad.", "request": False},

    # === ARMBANDEN ===
    {"slug": "armband-hexagon-zwarte-diamant", "name": "Armband hexagon met zwarte diamant", "category": "Armbanden", "material": "Rosé goud 18kt, diamant", "metal": "18 karaat rosé goud", "stone": "Zwarte diamant", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3387-480x480.jpg", "desc": "Een moderne armband met hexagonaal ontwerp sluiting, bezet met een zwarte diamant. Stoer en elegant tegelijk, geschikt als herensieraad.", "request": False},
    {"slug": "armband-zeshoek-sluiting", "name": "Armband met zeshoek design sluiting", "category": "Armbanden", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC3679-480x480.jpg", "desc": "Een geelgouden armband met een markante zeshoek als sluiting. Het geometrische ontwerp geeft dit klassieke sieraad een eigentijds karakter.", "request": False},
    {"slug": "minimalistische-cuff-armband", "name": "Minimalistische cuff armband", "category": "Armbanden", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/DSC_6452-End-480x480.jpg", "desc": "Een strakke, minimalistische cuff in geelgoud. De open band is comfortabel en past zich aan de pols aan. Kan opnieuw voor u gemaakt worden.", "request": True},
    {"slug": "geelgouden-schakelarmband", "name": "Geelgouden schakelarmband", "category": "Armbanden", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Elk schakeltje individueel gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/01-DSC_3345-End-480x480.jpg", "desc": "Een luxueuze schakelarmband waarbij elk schakeltje individueel met de hand is gesmeed. De soepele val en warme glans van geelgoud maken dit tot een tijdloos bezit.", "request": True},
    {"slug": "geelgouden-slavenarmband", "name": "Geelgouden slavenarmband", "category": "Armbanden", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/armband-slavenband-x11-480x480.jpg", "desc": "Een klassieke slavenarmband in 18 karaat geelgoud. De brede, ronde band is met de hand gehamerd voor een subtiele textuur.", "request": True},

    # === MANCHETKNOPEN ===
    {"slug": "primavera-manchetknopen-geelgoud", "name": "Primavera manchetknopen geelgoud", "category": "Manchetknopen", "material": "Geel goud 18kt", "metal": "18 karaat geelgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/10-DSC_5421-End-480x480.jpg", "desc": "De Primavera manchetknopen in warm geelgoud met een organisch, bloem-geïnspireerd ontwerp. Een subtiel statement aan elke manchet.", "request": False},
    {"slug": "primavera-manchetknopen-witgoud", "name": "Primavera manchetknopen witgoud", "category": "Manchetknopen", "material": "Wit goud 18kt", "metal": "18 karaat witgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/09-DSC_5409-End-480x480.jpg", "desc": "De Primavera manchetknopen in koel witgoud. Dezelfde organische vorm als de geelgouden versie, maar met een moderne, koele uitstraling.", "request": False},
    {"slug": "maansteen-manchetknopen", "name": "Maansteen manchetknopen", "category": "Manchetknopen", "material": "Rosé goud 18kt, maansteen", "metal": "18 karaat rosé goud", "stone": "Maansteen", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/01-DSC_4698-End-1-480x480.jpg", "desc": "Manchetknopen met maansteen in rosé goud. De mysterieuze adularescentie van maansteen maakt elke beweging van de manchet fascinerend.", "request": False},
    {"slug": "octopus-manchetknopen", "name": "Octopus manchetknopen", "category": "Manchetknopen", "material": "Geel goud 18kt, Zuidzee keshi parel", "metal": "18 karaat geelgoud", "stone": "Zuidzee keshi parel", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/manchetknopen-octopus-x11-480x480.jpg", "desc": "Speelse manchetknopen in de vorm van een octopus, met Zuidzee keshi parels. Een uniek ontwerp dat vakmanschap en humor combineert.", "request": False},
    {"slug": "parelmoer-manchetknopen", "name": "Parelmoer manchetknopen", "category": "Manchetknopen", "material": "Rosé goud 18kt, parelmoer", "metal": "18 karaat rosé goud", "stone": "Parelmoer", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/manchetknopen-parelmoer-x11-480x480.jpg", "desc": "Manchetknopen met schijfjes parelmoer in rosé goud. De iriserende glans van parelmoer geeft deze manchetknopen een verfijnd karakter.", "request": False},
    {"slug": "zeshoek-manchetknopen", "name": "Zeshoek manchetknopen", "category": "Manchetknopen", "material": "Rosé goud 18kt", "metal": "18 karaat rosé goud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/02-DSC_4708-End-480x480.jpg", "desc": "Geometrische manchetknopen met zeshoek ontwerp in rosé goud. Modern, grafisch en tijdloos. Passend bij de zeshoek armband.", "request": False},

    # === BROCHES ===
    {"slug": "dasspeld-makelaarsstaf", "name": "Dasspeld met makelaarsstaf", "category": "Broches", "material": "Wit goud 18kt", "metal": "18 karaat witgoud", "stone": None, "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/dasspeld-kandelaar-11-480x480.jpg", "desc": "Een witgouden dasspeld met een makelaarsstaf als motief. Een persoonlijk en betekenisvol sieraad voor bij het pak.", "request": False},
    {"slug": "saffier-broche", "name": "Saffier broche", "category": "Broches", "material": "Geel goud 18kt, saffier, diamant", "metal": "18 karaat geelgoud", "stone": "Saffier", "accent": "Diamant", "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/saffier-jabot-11-480x480.jpg", "desc": "Een imposante broche met saffier en diamant in geelgoud. Een draagbaar kunstwerk dat een outfit transformeert.", "request": True},
    {"slug": "vlieg-speldje", "name": "Vlieg speldje", "category": "Broches", "material": "Geel goud 18kt, saffier", "metal": "18 karaat geelgoud", "stone": "Saffier", "accent": None, "making": "Volledig met de hand gesmeed", "img": "https://wiewelgoudsmeden.nl/wp-content/uploads/2015/06/dasspeld-vlieg-11-480x480.jpg", "desc": "Een gedetailleerd speldje in de vorm van een vlieg, met saffier ogen. Een speels en vakkundig vervaardigd sieraad dat gesprekken op gang brengt.", "request": False},
]

# ============================================================
# PDP TEMPLATE (without related items — "1 goed aanbieden")
# ============================================================

def pdp_template(p):
    slug = p['slug']
    name = p['name']
    cat = p['category']
    cat_lower = cat.lower()
    material = p['material']
    metal = p['metal']
    stone = p['stone']
    accent = p['accent']
    making = p['making']
    desc = p['desc']
    is_request = p['request']
    img_file = f"{slug}.jpg"

    # Badge HTML
    badge_html = ''
    if is_request:
        badge_html = '\n              <span class="pdp__badge pdp__badge--request">Op aanvraag</span>'

    # Specs
    specs = []
    specs.append(('Materiaal', metal))
    if stone:
        specs.append(('Centrale steen' if cat == 'Ringen' else 'Edelsteen', stone))
    if accent:
        specs.append(('Accent', accent))
    specs.append(('Vervaardiging', making))

    specs_html = '\n'.join([f'''              <div class="pdp__spec">
                <span class="pdp__spec-label">{label}</span>
                <span class="pdp__spec-value">{value}</span>
              </div>''' for label, value in specs])

    # CTA text
    if is_request:
        cta_text = 'Laat dit sieraad maken'
    else:
        cta_text = 'Informeer naar dit sieraad'

    # Description paragraph 2
    if is_request:
        desc_p2 = 'Dit sieraad kan opnieuw voor u worden vervaardigd. Neem contact op om de mogelijkheden te bespreken.'
    else:
        desc_p2 = 'Dit stuk is beschikbaar in ons atelier aan de Haven in Schoonhoven. Plan een afspraak om het in het echt te bekijken.'

    # Schema availability
    schema_avail = 'https://schema.org/PreOrder' if is_request else 'https://schema.org/InStock'

    # URL-encode name for contact link
    contact_param = name.replace(' ', '+')

    return f'''<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(name)} | Wiewel Goudsmeden Schoonhoven</title>
  <meta name="description" content="Handgemaakt sieraad: {html.escape(name)}. {html.escape(material)}. Vervaardigd door meestergoudsmid Wiewel in Schoonhoven.">
  <link rel="canonical" href="https://wiewelgoudsmeden.nl/collectie/{slug}.html">

  <!-- Open Graph -->
  <meta property="og:title" content="{html.escape(name)} | Wiewel Goudsmeden">
  <meta property="og:description" content="Handgemaakt sieraad: {html.escape(name)}. {html.escape(material)}.">
  <meta property="og:image" content="https://wiewelgoudsmeden.nl/assets/images/collectie/{img_file}">
  <meta property="og:url" content="https://wiewelgoudsmeden.nl/collectie/{slug}.html">
  <meta property="og:type" content="product">
  <meta property="og:locale" content="nl_NL">
  <meta property="og:site_name" content="Wiewel Goudsmeden">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(name)} | Wiewel Goudsmeden">
  <meta name="twitter:description" content="Handgemaakt sieraad: {html.escape(name)}. {html.escape(material)}.">
  <meta name="twitter:image" content="https://wiewelgoudsmeden.nl/assets/images/collectie/{img_file}">

  <!-- Preload critical fonts -->
  <link rel="preload" href="../assets/fonts/cormorant-garamond-600.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="../assets/fonts/catamaran-400.woff2" as="font" type="font/woff2" crossorigin>

  <link rel="stylesheet" href="../assets/style.css">

  <!-- JSON-LD: BreadcrumbList -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://wiewelgoudsmeden.nl/"
      }},
      {{
        "@type": "ListItem",
        "position": 2,
        "name": "Collectie",
        "item": "https://wiewelgoudsmeden.nl/collectie.html"
      }},
      {{
        "@type": "ListItem",
        "position": 3,
        "name": "{html.escape(name)}",
        "item": "https://wiewelgoudsmeden.nl/collectie/{slug}.html"
      }}
    ]
  }}
  </script>

  <!-- JSON-LD: Product -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "{html.escape(name)}",
    "description": "{html.escape(desc)}",
    "image": "https://wiewelgoudsmeden.nl/assets/images/collectie/{img_file}",
    "brand": {{
      "@type": "Brand",
      "name": "Wiewel Goudsmeden"
    }},
    "material": "{html.escape(material)}",
    "manufacturer": {{
      "@type": "Organization",
      "name": "Wiewel Goudsmeden",
      "url": "https://wiewelgoudsmeden.nl"
    }},
    "offers": {{
      "@type": "Offer",
      "availability": "{schema_avail}",
      "itemCondition": "https://schema.org/NewCondition",
      "seller": {{
        "@type": "Organization",
        "name": "Wiewel Goudsmeden"
      }}
    }}
  }}
  </script>
</head>
<body>

  <!-- ===== HEADER ===== -->
  <header class="header" role="banner">
    <div class="header__inner">
      <a href="/" class="header__logo" aria-label="Wiewel Goudsmeden - Naar homepage">
        <img src="../assets/images/logo-desktop.png" alt="Wiewel Goudsmeden logo" width="160" height="44">
        <div class="header__guild-badges">
          <a href="https://meestergoudsmeden.nl" target="_blank" rel="noopener" aria-label="Meestergoudsmeden"><img src="../assets/images/icon-gilde.png" alt="Meestergoudsmeden" width="28" height="28"></a>
          <a href="https://goudenzilversmidsgilde.nl" target="_blank" rel="noopener" aria-label="Gilde St. Eloy"><img src="../assets/images/gilde-st-eloy-white.png" alt="Gilde St. Eloy" width="28" height="28"></a>
        </div>
      </a>
      <nav class="header__nav" aria-label="Hoofdnavigatie">
        <a href="/">Home</a>
        <a href="../collectie.html" class="active">Collectie</a>
        <a href="../werk-in-opdracht.html">Maatwerk</a>
        <div class="header__dropdown">
          <a href="#" class="header__dropdown-toggle" aria-haspopup="true">Diensten <svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></a>
          <div class="header__dropdown-menu">
            <a href="../reparatie.html">Reparatie</a>
            <a href="../restauratie.html">Restauratie</a>
          </div>
        </div>
        <a href="../over-wiewel.html">Over ons</a>
        <a href="../contact.html">Contact</a>
      </nav>
      <div class="header__contact">
        <a href="tel:+31850668950" class="header__phone" aria-label="Bel ons: 085-066 8950">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.58.57 1 1 0 011 1v3.49a1 1 0 01-1 1A17 17 0 013 5a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.58 1 1 0 01-.25 1.01l-2.2 2.2z"/></svg>
          085-066 8950
        </a>
        <a href="../contact.html#afspraak" class="header__cta">Plan een afspraak</a>
      </div>
      <button class="header__burger" aria-label="Menu openen" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <!-- Mobile navigation -->
  <nav class="mobile-nav" aria-label="Mobiele navigatie">
    <a href="/">Home</a>
    <a href="../collectie.html" class="active">Collectie</a>
    <a href="../werk-in-opdracht.html">Maatwerk</a>
    <a href="../reparatie.html">Reparatie</a>
    <a href="../restauratie.html">Restauratie</a>
    <a href="../over-wiewel.html">Over ons</a>
    <a href="../contact.html">Contact</a>
    <a href="tel:+31850668950" class="mobile-nav__phone">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="#cea057" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.58.57 1 1 0 011 1v3.49a1 1 0 01-1 1A17 17 0 013 5a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.58 1 1 0 01-.25 1.01l-2.2 2.2z"/></svg>
      085-066 8950
    </a>
    <a href="../contact.html#afspraak" class="mobile-nav__cta">Plan een afspraak</a>
  </nav>

  <main>
    <!-- ===== BREADCRUMB ===== -->
    <div class="breadcrumb-strip">
      <div class="container">
        <nav class="breadcrumb" aria-label="Kruimelpad">
          <a href="/">Home</a> <span aria-hidden="true">&rsaquo;</span> <a href="../collectie.html">Collectie</a> <span aria-hidden="true">&rsaquo;</span> {html.escape(name)}
        </nav>
      </div>
    </div>

    <!-- ===== PRODUCT DETAIL ===== -->
    <section class="pdp" aria-label="Product detail">
      <div class="container">
        <div class="pdp__layout">
          <!-- Image -->
          <div class="pdp__gallery">
            <div class="pdp__image-main">
              <img src="../assets/images/collectie/{img_file}" alt="{html.escape(name)}, {html.escape(material)}" width="800" height="800" decoding="async">{badge_html}
            </div>
          </div>

          <!-- Info -->
          <div class="pdp__info">
            <p class="pdp__category"><a href="../collectie.html#{cat_lower}">{html.escape(cat)}</a></p>
            <h1 class="pdp__title">{html.escape(name)}</h1>
            <p class="pdp__subtitle">{html.escape(material)}</p>

            <div class="pdp__description">
              <p>{html.escape(desc)}</p>
              <p>{desc_p2}</p>
            </div>

            <!-- Specs -->
            <div class="pdp__specs">
{specs_html}
            </div>

            <!-- CTA -->
            <div class="pdp__cta-block">
              <a href="../contact.html?onderwerp={contact_param}" class="btn btn--gold pdp__cta-btn">
                {cta_text}
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </a>
              <p class="pdp__cta-note">Of mail ons: <a href="mailto:info@wiewelgoudsmeden.nl">info@wiewelgoudsmeden.nl</a></p>
            </div>

            <!-- Trust signals -->
            <div class="pdp__trust">
              <div class="pdp__trust-item">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2L3 7v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M9 12l2 2 4-4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                <span>Certificaat van echtheid</span>
              </div>
              <div class="pdp__trust-item">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 100 20 10 10 0 000-20z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 12h8M12 8v8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                <span>Persoonlijk advies op afspraak</span>
              </div>
              <div class="pdp__trust-item">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
                <span>Handgemaakt in Schoonhoven</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== CRAFTSMANSHIP STRIP ===== -->
    <section class="pdp-craft section--alt" aria-label="Vakmanschap">
      <div class="container">
        <div class="pdp-craft__inner">
          <div class="pdp-craft__text">
            <h2>Vervaardigd door meestergoudsmeden</h2>
            <p>Elk sieraad van Wiewel is volledig met de hand vervaardigd in ons atelier. Van het smelten van het edelmetaal tot het zetten van de laatste steen. Geen massaproductie, geen machines. Alleen ambacht, geduld en vakmanschap dat van generatie op generatie is doorgegeven.</p>
            <a href="../werk-in-opdracht.html" class="pdp-craft__link">Meer over ons maatwerk <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg></a>
          </div>
          <div class="pdp-craft__img">
            <img src="../assets/images/process-2.jpg" alt="Meestergoudsmid aan het werk in het atelier" loading="lazy" width="600" height="400" decoding="async">
          </div>
        </div>
      </div>
    </section>

    <!-- ===== CTA BANNER ===== -->
    <section class="cta-banner" aria-label="Afspraak maken">
      <div class="container">
        <h2>Wilt u dit sieraad in het echt bekijken?</h2>
        <p>Plan een afspraak in ons atelier in Schoonhoven. Wij nemen alle tijd om u persoonlijk te adviseren.</p>
        <a href="../contact.html#afspraak" class="btn btn--gold">Plan een afspraak</a>
      </div>
    </section>
  </main>

  <!-- ===== FOOTER ===== -->
  <footer class="footer" role="contentinfo">
    <div class="container">
      <div class="footer__grid">
        <div class="footer__brand">
          <img src="../assets/images/logo-white.png" alt="Wiewel Goudsmeden logo" width="160" height="48">
          <p>Handgemaakte sieraden door meestergoudsmeden in Schoonhoven. Twee generaties vakmanschap, traditioneel ambacht en eigentijds design sinds 1980.</p>
          <div class="footer__guild">
            <img src="../assets/images/gilde-st-eloy.png" alt="Gilde Sint Eloy logo" width="40" height="40">
            <img src="../assets/images/logo-ngg.png" alt="Nederlands Goudsmeden Genootschap logo" width="40" height="40">
          </div>
        </div>
        <div>
          <h4>Navigatie</h4>
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="../collectie.html">Collectie</a></li>
            <li><a href="../werk-in-opdracht.html">Maatwerk</a></li>
            <li><a href="../over-wiewel.html">Over ons</a></li>
            <li><a href="../contact.html">Contact</a></li>
          </ul>
        </div>
        <div>
          <h4>Diensten</h4>
          <ul>
            <li><a href="../werk-in-opdracht.html">Sieraden op maat</a></li>
            <li><a href="../reparatie.html">Reparatie</a></li>
            <li><a href="../restauratie.html">Restauratie</a></li>
          </ul>
        </div>
        <div>
          <h4>Contact</h4>
          <ul>
            <li>Haven 70</li>
            <li>2871 CR Schoonhoven</li>
            <li><a href="tel:+31850668950">085-066 8950</a></li>
            <li><a href="mailto:info@wiewelgoudsmeden.nl">info@wiewelgoudsmeden.nl</a></li>
          </ul>
          <div class="footer__social">
            <a href="https://www.instagram.com/wiewelgoudsmeden/" target="_blank" rel="noopener" aria-label="Volg ons op Instagram">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 01-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 017.8 2zm-.2 2A3.6 3.6 0 004 7.6v8.8C4 18.39 5.61 20 7.6 20h8.8a3.6 3.6 0 003.6-3.6V7.6C20 5.61 18.39 4 16.4 4H7.6zm9.65 1.5a1.25 1.25 0 110 2.5 1.25 1.25 0 010-2.5zM12 7a5 5 0 110 10 5 5 0 010-10zm0 2a3 3 0 100 6 3 3 0 000-6z"/></svg>
            </a>
          </div>
        </div>
      </div>
      <div class="footer__bottom">
        <span>&copy; 2026 Wiewel Goudsmeden. Alle rechten voorbehouden.</span>
        <a href="../privacy.html">Privacyverklaring</a>
      </div>
    </div>
  </footer>

  <!-- ===== COOKIE CONSENT ===== -->
  <div class="cookie-banner" id="cookieBanner" role="dialog" aria-label="Cookie instellingen">
    <div class="cookie-banner__inner">
      <p>Wij gebruiken cookies om uw ervaring te verbeteren en ons websiteverkeer te analyseren. Lees meer in onze <a href="../privacy.html">privacyverklaring</a>.</p>
      <div class="cookie-banner__btns">
        <button class="cookie-banner__accept" onclick="acceptCookies()">Accepteren</button>
        <button class="cookie-banner__decline" onclick="declineCookies()">Weigeren</button>
      </div>
    </div>
  </div>

  <script src="../assets/analytics.js" defer></script>
</body>
</html>'''


# ============================================================
# DOWNLOAD IMAGES
# ============================================================

def download_image(url, dest_path):
    if os.path.exists(dest_path):
        print(f"  [skip] {os.path.basename(dest_path)} (exists)")
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(dest_path, 'wb') as f:
                f.write(resp.read())
        print(f"  [ok]   {os.path.basename(dest_path)}")
        return True
    except Exception as e:
        print(f"  [FAIL] {os.path.basename(dest_path)}: {e}")
        return False


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print(f"=== Generating {len(PRODUCTS)} PDPs ===\n")

    # 1. Download images
    print("--- Downloading images ---")
    ok = 0
    fail = 0
    for p in PRODUCTS:
        dest = os.path.join(IMG_DIR, f"{p['slug']}.jpg")
        if download_image(p['img'], dest):
            ok += 1
        else:
            fail += 1
    print(f"\nImages: {ok} ok, {fail} failed\n")

    # 2. Generate PDPs
    print("--- Generating PDP HTML ---")
    for p in PRODUCTS:
        path = os.path.join(COLLECTIE_DIR, f"{p['slug']}.html")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(pdp_template(p))
        print(f"  [ok] {p['slug']}.html")

    print(f"\nDone! Generated {len(PRODUCTS)} PDPs in collectie/")
    print(f"Images saved to assets/images/collectie/")

    # 3. Summary by category
    cats = {}
    for p in PRODUCTS:
        cats.setdefault(p['category'], []).append(p)
    print("\n--- Summary ---")
    for cat, items in cats.items():
        request_count = sum(1 for i in items if i['request'])
        print(f"  {cat}: {len(items)} items ({request_count} op aanvraag)")
