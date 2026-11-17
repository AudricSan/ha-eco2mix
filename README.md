# 🔌 éCO2mix pour Home Assistant

Cette intégration Home Assistant vous permet d'accéder aux données RTE (Réseau de Transport d'Électricité) via l'API éCO2mix, offrant une vue détaillée du réseau électrique français.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintained](https://img.shields.io/maintenance/yes/2024.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Dashboard Preview](https://raw.githubusercontent.com/lfpoulain/ha-eco2mix/refs/heads/main/images/dashboard.png)

## ✨ Fonctionnalités

- 📈 Suivi en temps réel de la consommation électrique
- 🔋 Détail de la production par source d'énergie
- 🔄 Monitoring des échanges internationaux (Import/Export)
- 📊 Visualisations dynamiques du mix énergétique
- 📱 Dashboard intégré et responsive
- ⚡ Conversion automatique en GigaWatts

## 📋 Prérequis

1. 🏠 Une installation Home Assistant **2024.12** fonctionnelle
2. 🛠️ HACS (Home Assistant Community Store)
3. 📊 Cartes personnalisées (via HACS) :
   - 📈 apexcharts-card
   - 🥧 pie-chart-card

## 🚀 Installation

### Via HACS (Recommandé) 

1. Dans HACS > Intégrations
2. Menu ⋮ > Dépôts personnalisés
3. Ajouter `https://github.com/lfpoulain/ha-eco2mix`
4. Sélectionner "Intégration"
5. Rechercher "éCO2mix"
6. Installer et redémarrer Home Assistant

![Installation Steps](https://raw.githubusercontent.com/lfpoulain/ha-eco2mix/refs/heads/main/images/installation.png)

### Installation Manuelle 🛠️

1. 📥 Télécharger le dépôt
2. 📁 Copier `custom_components/eco2mix` dans votre dossier `custom_components`
3. 🔄 Redémarrer Home Assistant

## ⚙️ Configuration

1. Aller dans Configuration > Intégrations
2. Cliquer sur le bouton "+" 
3. Rechercher "éCO2mix"
4. Ajoutez l'intégration 
5. Choisissez la source : France (aucun réglage) ou Japon (puis la zone, voir [Japon / Japan](#-japon--japan))

## 📊 Dashboard

Un dashboard d'exemple est disponnible : [eco2mix.yaml](https://github.com/lfpoulain/ha-eco2mix/blob/main/dashboards/eco2mix.yaml)

![Main View](https://raw.githubusercontent.com/lfpoulain/ha-eco2mix/refs/heads/main/images/main_view.png)

- 📊 Valeurs principales en GW
- 📈 Graphique d'évolution 24h
- 🥧 Répartition de la production

> Il faudra probablement modifier les entités utilisé dans le dashboard car elles peuvent être nommées différemment sur votre homeassistant

### Sources d'Énergie Suivies

| Source | Icône |
|--------|-------|
| Nucléaire | ⚛️ |
| Éolien | 🌪️ |
| Solaire | ☀️ |
| Hydraulique | 💧 |
| Bioénergies | 🌱 |
| Gaz | 🔥 |
| Charbon | 🏭 |
| Fioul | 🛢️ |

## 🇯🇵 Japon / Japan

L'intégration gère aussi le Japon via les CSV officiels **でんき予報** (prévision d'électricité) publiés par les gestionnaires de réseau. Choisissez « 日本 / Japon » à l'ajout, puis la zone : **une entrée par zone** (la France reste limitée à une entrée).

### Zones et sources vérifiées

Toutes les zones utilisent le même format CSV (Shift_JIS/CP932, valeurs en 万kW converties en MW). L'URL contient `{date}` = AAAAMMJJ en heure japonaise pour les compagnies qui publient un fichier par jour.

| Zone | Gestionnaire (出典) | URL du CSV |
|---|---|---|
| 北海道 Hokkaido | 北海道電力ネットワーク | `https://denkiyoho.hepco.co.jp/area/data/juyo_01_{date}.csv` |
| 東北 Tohoku | 東北電力ネットワーク | `https://setsuden.nw.tohoku-epco.co.jp/common/demand/juyo_02_{date}.csv` |
| 東京 Tokyo (Kantō) | 東京電力パワーグリッド | `https://www.tepco.co.jp/forecast/html/images/juyo-d1-j.csv` |
| 中部 Chubu | 中部電力パワーグリッド | `https://powergrid.chuden.co.jp/denki_yoho_content_data/juyo_cepco003.csv` |
| 北陸 Hokuriku | 北陸電力送配電 | `https://www.rikuden.co.jp/nw/denki-yoho/csv/juyo_05_{date}.csv` |
| 関西 Kansai | 関西電力送配電 | `https://www.kansai-td.co.jp/yamasou/juyo_06_{date}.csv` |
| 中国 Chugoku | 中国電力ネットワーク | `https://www.energia.co.jp/nw/jukyuu/sys/juyo_07_{date}.csv` |
| 四国 Shikoku | 四国電力送配電 | `https://www.yonden.co.jp/nw/denkiyoho/juyo_08_{date}.csv` |
| 九州 Kyushu | 九州電力送配電 | `https://www.kyuden.co.jp/td_power_usages/csv/juyo-hourly-{date}.csv` |
| 沖縄 Okinawa | 沖縄電力 | `https://www.okiden.co.jp/denki2/juyo_10_{date}.csv` |

Notes : pour Kansai, l'ancien `juyo1_kansai.csv` n'est plus mis à jour (contenu de décembre 2025) ; le nom du jour est donné par `/yamasou/jisseki-latest.json`. Pour Shikoku, `juyo_shikoku.csv` n'existe pas (404) ; le fichier du jour est `juyo_08_{date}.csv`.

### Capteurs (un appareil par zone)

Un capteur n'est créé que si la zone publie la mesure correspondante.

| Capteur | Source dans le CSV |
|---|---|
| Consommation (MW) | dernière valeur non vide de 当日実績 (5 min, sinon horaire) |
| Prévision de consommation (MW) | 予測値 / 予想値 du créneau horaire courant |
| Capacité de fourniture (MW) | 供給力 du créneau horaire courant |
| Taux d'utilisation (%) | 使用率 de la dernière heure réalisée |
| Pic de consommation prévu (MW) | 予想最大電力 (+ créneau en attribut `slot`) |
| Capacité de fourniture à la pointe (MW) | ピーク時供給力 |
| Réserve à la pointe (%) | ピーク時予備率 |
| Production solaire (MW) | 太陽光発電実績 (5 min) |
| Production éolienne (MW) | 風力発電実績, **Tohoku uniquement** |

Attributs : `area`, `source_url`, `csv_updated` (heure de mise à jour de l'en-tête du CSV, JST), et l'heure/le créneau de la mesure. Les CSV sont découpés en blocs lus **par nom de colonne** (jamais par numéro de ligne) ; les blocs « 翌日 » (lendemain) sont ignorés. Le rafraîchissement est de 5 minutes.

### Limites

- Il n'y a **pas de mix de production par filière** (nucléaire, gaz, charbon…) en temps réel au Japon : les données publiques sont différées. Seuls le solaire (et l'éolien à Tohoku) sont fournis.
- Le solaire est une production **réalisée dans la zone** mesurée par le gestionnaire (valeur 0 la nuit).
- 使用率 est la valeur publiée pour la dernière heure complète, donc légèrement décalée par rapport à la consommation 5 min.
- Le fichier du jour peut manquer juste après minuit JST : les capteurs passent alors « indisponible » jusqu'à la publication.

### Tests

```bash
python -m venv .venv && .venv/Scripts/python -m pip install pytest
.venv/Scripts/python -m pytest -q
```

Le parseur (`custom_components/eco2mix/jp_parser.py`) n'a aucune dépendance à Home Assistant ; les fichiers réels de chaque zone sont dans `tests/fixtures/`.

### English summary

Japan support: pick "日本 / Japon" when adding the integration, then one of the 10 general transmission areas (Hokkaido, Tohoku, Tokyo/TEPCO, Chubu, Hokuriku, Kansai, Chugoku, Shikoku, Kyushu, Okinawa). One config entry per area; France stays limited to one entry. Data comes from each utility's official **でんき予報** CSV (Shift_JIS, 万kW converted to MW), polled every 5 minutes with `aiohttp`. Sensors (created only if the area publishes them): current consumption, forecast, supply capacity, utilization rate, forecast peak demand, supply capacity at peak, reserve margin at peak, solar output (and wind output for Tohoku). There is no real-time generation mix by fuel type in Japan (public data is delayed). Data © each utility listed above (出典: 各一般送配電事業者「でんき予報」).

## ❓ Dépannage

Si les données ne s'affichent pas :
1. 🔍 Vérifier votre connexion Internet
2. 📝 Consulter les logs Home Assistant
3. 🔄 Redémarrer Home Assistant

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- 🐛 Signaler des bugs
- 💡 Proposer des améliorations
- 🔧 Soumettre des pull requests

## 📫 Support

Besoin d'aide ? 
- 📝 Ouvrir une [Issue](https://github.com/lfpoulain/ha-eco2mix/issues)
- 💬 Rejoindre la discussion

## 👏 Crédits

- ⚡ Données : [RTE éCO2mix](https://www.rte-france.com/eco2mix)
- 🌐 API : [ODRE](https://odre.opendatasoft.com/)

## 📄 Licence

Ce projet est sous licence MIT. Consultez le fichier LICENSE pour plus de détails.

---
Made with ❤️ by [@lfpoulain](https://github.com/lfpoulain)
And with the generous help of [@piitaya](https://github.com/piitaya)
