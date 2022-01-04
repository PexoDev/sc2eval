from keras.backend import reshape
from keras.models import _reset_build_compile_trackers
from zephyrus_sc2_parser.game import player
from player import Player
from replayDataPoint import ReplayDataPoint

import os
import json
import threading
import time
import Zephyrus.parser as zp
import numpy as np
import sklearn as skl
import shutil


ReplaysFolder = "M:/Uni/sc2eval/Replays"
CorruptedReplaysFolder = "M:/Uni/sc2eval/CorruptedReplays"
TooShortReplaysFolder = "M:/Uni/sc2eval/TooShortReplays"
SerializedDataFolder = "M:/Uni/sc2eval/SerializedData"

CorruptedReplays = ['!!!!!!!!.SC2Replay', '#1_TIMONEN_vs_nunu_Frozen_Temple.SC2Replay', '#5 TvP Turret 2 Base Push vs Phoenix.SC2Replay', '#Respect.SC2Replay', '$$$Fastest Map$$$.SC2Replay', '(L) PvZ Frozen Temple Gas Stolen and then overwhelmed by Hydras.SC2Replay', '(P)Larry,(Z)Ares VS (P)puCK,(Z)Bioice.SC2Replay', '(P)Larry,(Z)Ares VS (Z)Bioice,(P)puCK.SC2Replay', '(P)Night,(T)Lillekanin VS (Z)CatZ,(T)Kelazhur (1).SC2Replay', '(P)Night,(T)Lillekanin VS (Z)CatZ,(T)Kelazhur.SC2Replay', '(T)Semper,(P)poizon VS (P)Lightning,(P)NightEnD (1).SC2Replay', '(T)Semper,(P)poizon VS (P)Lightning,(P)NightEnD.SC2Replay', '(T)Semper,(P)poizon VS (P)Lightning,(T)NightEnD.SC2Replay', '(Z)Ares,(P)Larry VS (P)CranK,(Z)True (1).SC2Replay', '(Z)Ares,(P)Larry VS (P)CranK,(Z)True.SC2Replay', '(Z)Ares,(P)Larry VS (Z)Bioice,(P)puCK.SC2Replay', '(Z)Nerchio,(Z)Elazer VS (P)Night,(T)Lillekanin.SC2Replay', '(Z)Nerchio,(Z)Elazer VS (T)Beastyqt,(T)FeelsBanjo.SC2Replay', '(Z)Nerchio,(Z)Elazer VS (T)Lillekanin,(P)Night.SC2Replay', '(Z)Nerchio,(Z)Elazer VS (T)Lillekanin,(Z)Night.SC2Replay', '(Z)Nerchio,(Z)Elazer VS (Z)RNGeus,(T)Goosejuice (1).SC2Replay', '(Z)Nerchio,(Z)Elazer VS (Z)RNGeus,(T)Goosejuice.SC2Replay', '(Z)Night,(T)Lillekanin VS (Z)Nerchio,(Z)Elazer.SC2Replay', '(Z)PengWin,(T)Smile VS (Z)True,(P)CranK (1).SC2Replay', '(Z)PengWin,(T)Smile VS (Z)True,(P)CranK.SC2Replay', '++++-+.SC2Replay', '++ΓÇ║8-ΓÇ║+ΓÇ║ (2).SC2Replay', '++ΓÇ║8-ΓÇ║+ΓÇ║ (2)_1.SC2Replay', '++ΓÇ║8-ΓÇ║+ΓÇ║ (2)_2.SC2Replay', '++ΓÇ║8-ΓÇ║+ΓÇ║ iGMacSed vs iGXiGua ( WIN).SC2Replay', '++ΓÇ║8-ΓÇ║+ΓÇ║ [Thpj]+╦¥+s-ΓÇ║-8-E╠é+╦Ö-+ vs iGiA (iGiA WIN).SC2Replay', '+1 roach timing.SC2Replay', '+1Carapace Timing Attack vs Adeptoss.SC2Replay', '+Γäó+Γëá-ΓÇ║+--E╠é (2).SC2Replay', '+Γäó+Γëá-ΓÇ║+--E╠é [Bheart]+Γäó++-ΓäóΓÇ║=+┬╢ΓÇ║╦ÖΓÇ║-+ΓÇ║ vs [Hist]Psmoonsun (Psmoonsun WI.SC2Replay', '+Γäó+Γëá-ΓÇ║+--E╠é [Bheart]_~+--ΓÇ║ vs iGJim (iGJim WIN).SC2Replay', '+Γäó+Γëá-ΓÇ║+--E╠é [Hist]Cloudy vs [Thpj]+╦¥+s-ΓÇ║-8-E╠é+╦Ö-+ (+╦¥+s-ΓÇ║-8-E╠é+╦Ö-+ WIN).SC2Replay', '+Γäó+Γëá-ΓÇ║+--E╠é(iGXiGua, iGMacSed WIN).SC2Replay', '+Γäó+Γëá-ΓÇ║+--E╠é.SC2Replay', '+ΓÇ║+=+Γëá+-+├åΓÇ║+ (4).SC2Replay', '+ΓÇ║+=+Γëá+-+├åΓÇ║+ iGXiGua vs iGRushcrazy (iGMacSed, iGXiGua WIN).SC2Replay', '+ΓÇ║+=+Γëá+-+├åΓÇ║+ [Thpj]+╦¥+s-ΓÇ║-8-E╠é+╦Ö-+ vs iGRushcrazy (iGXY, +╦¥+s-ΓÇ║-8-E╠é+╦Ö-+ .SC2Replay', '---------- ADONMINUS FINAL PvP ---------------.SC2Replay', '------------- ADONMINUS FINAL PvT Demuslim ----------------.SC2Replay', '--------------- ADONMINUS FINAL PvZ ------------------.SC2Replay', '--------------- ADONMINUS PvP ----------------.SC2Replay', '----------------- ADONMINUS PvZ FINAL NAUCIT --------------------.SC2Replay', '------------------- ADONMINUS PVT 2 -------------------------.SC2Replay', '-4 TvP New Gettysburg 1 Cyclone into 4 Medivac Opening vs Immortal Stalker Sentry.SC2Replay', '-Card Shuffle- (2).SC2Replay', '-Card Shuffle- (3).SC2Replay', '-Card Shuffle- (4).SC2Replay', '-Card Shuffle- (5).SC2Replay', '-Card Shuffle- (6).SC2Replay', '-Card Shuffle- (7).SC2Replay', '-Card Shuffle-.SC2Replay', '-Mafia- (475).SC2Replay', '-ΓÇ║+┬┤+├å-ΓÇ║ (2).SC2Replay', '-ΓÇ║+┬┤+├å-ΓÇ║ iGJim vs iGRushcrazy (iGJim WIN).SC2Replay', '-ΓÇ║+┬┤+├å-ΓÇ║ iGMacSed vs iGRushcrazy (iGXiGua, iGMacSed WIN).SC2Replay', '-ΓÇ║+┬┤+├å-ΓÇ║ [Bheart]+Γäó++-ΓäóΓÇ║=+┬╢ΓÇ║╦ÖΓÇ║-+ΓÇ║ vs [Bheart]doudou (iGXiGua, iGMacSed.SC2Replay', '-ΓÇ║+┬┤+├å-ΓÇ║ [Thpj]+╦¥+s-ΓÇ║-8-E╠é+╦Ö-+ vs [Hist]Cloudy (iGXY, +╦¥+s-ΓÇ║-8-E╠é+╦Ö-+ WIN).SC2Replay', '.SC2Replay', '0 (1).SC2Replay', '0 (2).SC2Replay', '0.SC2Replay', '000a4ab29a10c7db1e2e7d0dcde9aad01fb297a703417c03e4a5137c0fb2af0d.SC2Replay', '00c8d0873eda184cf69ea9f004ef7418c91020ea09061a185228a9b8d279aa49.SC2Replay', '01 - UB Ro4 - TIME vs Cyan - G2 - Oxide LE.SC2Replay', '01 - UB Ro4 - TIME vs Cyan - G3 - Jagannatha LE.SC2Replay', '01 - UB Ro4 - TIME vs Cyan - G4 - Lightshade LE.SC2Replay', '02 - PvZ (Central Protocol) - [FoFoG]Multi vs [HyperX]LiquidSnute.SC2Replay', '02 - PvZ (Central Protocol) - [FoFoG]Multi vs [HyperX]LiquidSnute_1.SC2Replay', '02 - UB Ro4 - Jieshi vs XY - G2 - Lightshade LE.SC2Replay', '03 - LB Ro2#1 - Cyan vs Jieshi - G2 - Oxide LE.SC2Replay', '03 - LB Ro2#1 - Cyan vs Jieshi - G3 - Jagannatha LE.SC2Replay', '03 - LB Ro2#1 - Cyan vs Jieshi - G4 - Romanticide LE.SC2Replay', '03roachhydra_massair.SC2Replay', '04 - UBF - TIME vs XY - G3 - Romanticide LE.SC2Replay', '05 - LBF - XY vs Cyan - G2 - Romanticide LE.SC2Replay', '05 - LBF - XY vs Cyan - G4 - Lightshade LE.SC2Replay', '05 - LBF - XY vs Cyan - G5 - Oxide LE.SC2Replay', '06 - GF - TIME vs XY - G2 - Oxide LE.SC2Replay', '0856a5a993e1c750.SC2Replay', '0a0f62052fe4311368910ad38c662bf979e292b86ad02b49b41a87013e58c432.SC2Replay', '0a1b09abc9e98f4e0c3921ae0a427c27e97c2bbdcf34f50df18dc41cea3f3249.SC2Replay', '1 1 1 hellion reaper into banshee cloack.SC2Replay', '1 base cancer mech.SC2Replay', '1 Base Liberator Opening into Expand with Helions.SC2Replay', '1 Base Liberator Opening into Expand.SC2Replay', '1 Base Liberator Opening into Expand_1.SC2Replay', '1 base muta zvt lotv.SC2Replay', '1 base ravager all in.SC2Replay', '1 Gate Fast expand to StarGate.SC2Replay', '1 Hour of Zombiefest on Metalopolis.SC2Replay', '1 thank you for the creep.SC2Replay', '1-1-1 Early expo.SC2Replay', '1-1-1 hellion lib into 5-1-1.SC2Replay', '10 minute Gold ZvP.SC2Replay', '109c4f1f6a8c886c.SC2Replay', '11 Roach Rush.SC2Replay', '1100 IQ memes ZvZ.SC2Replay', '111 Terran Build.SC2Replay', '111.SC2Replay', '11111.SC2Replay', '11240---Arid_Wastes.SC2Replay', '11242---Dusk_Towers.SC2Replay', '11244---Orbital_Shipyard.SC2Replay', '11246---Dusk_Towers.SC2Replay', '11248---Dusk_Towers.SC2Replay', '11249---Lerilak_Crest.SC2Replay', '11250---Dusk_Towers.SC2Replay', '11251---Dusk_Towers.SC2Replay', '11253---Prion_Terraces.SC2Replay', '11279---Dusk_Towers.SC2Replay', '11321---Dusk_Towers.SC2Replay', '11325---Prion_Terraces.SC2Replay', '11330---Dusk_Towers.SC2Replay', '11331---Lerilak_Crest.SC2Replay', '11333---Ruins_of_Seras.SC2Replay', '11367---Ulrena.SC2Replay', '12 pool vs proxy 4 gate into draw.SC2Replay', '12 pool zvp - TheZergLord.SC2Replay', '12 pool.SC2Replay', '123_1.SC2Replay', '12D速狗毒爆.SC2Replay', '12nvader LE_Goblins.SC2Replay', '13 gas pool .SC2Replay', '14 14 using 12 13 lingban harass.SC2Replay', '1414 vs master terran.SC2Replay', '14p into roach ravager muta vs adpt immo allin.SC2Replay', '15 15 - Moonlight Madness LE (Void) (2).SC2Replay', '15-11-18 21_04_09 [TvP] Orbital Shipyard.SC2Replay', '15-11-21 15_36_51 [PvZ] Lerilak Crest.SC2Replay', '15-11-25 aSim vs State [ZvP] Orbital Shipyard.SC2Replay', '15-11-25 Classic vs State [PvP] Central Protocol.SC2Replay', '15-11-25 INnoVation vs State [TvP] Prion Terraces.SC2Replay', '15-11-25 lIlIlIlIlI vs State [ZvP] Central Protocol.SC2Replay', '15-11-25 llllllllllll vs State [PvP] Orbital Shipyard.SC2Replay', '15-11-25 llllllllllll vs State [PvP] Ruins of Seras.SC2Replay', '15-11-25 llllllllllll vs State [TvP] Dusk Towers.SC2Replay', '15-11-25 llllllllllll vs State [TvP] Lerilak Crest.SC2Replay', '15-11-25 llllllllllll vs State [TvP] Orbital Shipyard (2).SC2Replay', '15-11-25 llllllllllll vs State [TvP] Prion Terraces (2).SC2Replay', '15-11-25 llllllllllll vs State [ZvP] Central Protocol.SC2Replay', '15-11-25 llllllllllll vs State [ZvP] Lerilak Crest (2).SC2Replay', '15-11-25 Rendezvous vs State [ZvP] Orbital Shipyard.SC2Replay', '15-11-25 sKyHigh vs State [TvP] Ulrena.SC2Replay', '15-11-25 Spirit vs State [TvP] Prion Terraces.SC2Replay', '15-11-25 State vs A.I. 1 (Very Easy) [PvZ] Dusk Towers.SC2Replay', '15-11-25 State vs AID [PvP] Ruins of Seras (2).SC2Replay', '15-11-25 State vs Classic [PvP] Ruins of Seras (2).SC2Replay', '15-11-25 State vs Cloudy [PvP] Dusk Towers (2).SC2Replay', '15-11-25 State vs GuMiho [PvT] Lerilak Crest.SC2Replay', '15-11-25 State vs IIIIIIIIIIII [PvZ] Lerilak Crest (2).SC2Replay', '15-11-25 State vs llllllllllll [PvT] Dusk Towers.SC2Replay', '15-11-25 State vs llllllllllll [PvT] Prion Terraces.SC2Replay', '15-11-25 State vs llllllllllll [PvT] Ruins of Seras (2).SC2Replay', '15-11-25 State vs llllllllllll [PvZ] Dusk Towers (2).SC2Replay', '15-11-25 State vs llllllllllll [PvZ] Dusk Towers.SC2Replay', '15-11-25 State vs [dPix]Patience [PvP] Orbital Shipyard (2).SC2Replay', '15-11-25 State vs [NEX]타토스 [PvT] Lerilak Crest (2).SC2Replay', '15-11-25 State vs [TF]Nemo [PvP] Dusk Towers.SC2Replay', '15-11-25 State vs [얼라이브]aLive [PvT] Orbital Shipyard.SC2Replay', '15-11-25 State vs 아마추어 [PvP] Dusk Towers.SC2Replay', '15-11-25 State vs 중추석 [PvP] Orbital Shipyard.SC2Replay', '15-11-25 Stork vs State [PvP] Dusk Towers (2).SC2Replay', '15-11-25 Stork vs State [PvP] Prion Terraces (2).SC2Replay', '15-11-25 [Wally]Wally vs State [ZvP] Orbital Shipyard.SC2Replay', '15-11-25 [Wally]Wally vs State [ZvP] Ulrena.SC2Replay', '15-11-25 [일반인원탑]MieroFiber vs State [TvP] Prion Terraces.SC2Replay', '15-11-30 22_02_51 [TvZ] Chantier naval orbitalSenryakku, IA (élite).SC2Replay', '15-11-30 23_47_28 [ZvT] Chantier naval orbitalDre, Senryakku.SC2Replay', '15-12-01 00_22_26 [TvZ] Chantier naval orbitalSenryakku, Swarm.SC2Replay', '15-12-01 01_59_44 [TvZ] UlrenaSenryakku, TheSixPaths.SC2Replay', '15-12-01 02_37_42 [ZvT] Ruines de SerasMAAPK, Senryakku.SC2Replay', '15-12-01 23_47_20 [ZvT] Crête de Lerilaknybbler, Senryakku.SC2Replay', '15-12-02 23_37_31 [ZvT] UlrenaTrigger, Senryakku.SC2Replay', '15-12-09 llllllllllll vs State [ZvP] Dusk Towers (2).SC2Replay', '15-12-09 llllllllllll vs State [ZvP] Dusk Towers.SC2Replay', '15-12-09 State vs llllllllllll [PvZ] Ulrena.SC2Replay', '15-12-09 State vs [DnG]Vaisravana [PvZ] Ulrena.SC2Replay', '15-12-09 [s2Mc]Curry vs State [ZvP] Dusk Towers.SC2Replay', '15-12-29 14_46_22 [PvP] Dusk Towers (2).SC2Replay', '15-12-29 15_48_26 [TvP] Dusk Towers (2).SC2Replay', '15-16-17 ling bane muta.SC2Replay', '15Hatch 14Gas 14Pool.SC2Replay', '16 bits EE (2).SC2Replay', '16 bits EE.SC2Replay', '16 Bits LE (2).SC2Replay', '16 Bits LE (4).SC2Replay', '16 Bits LE.SC2Replay', '16 Nexus Stalker Warpgate-Research.SC2Replay', '16 бит РВ (2).SC2Replay', '16 бит РВ (63).SC2Replay', '16-01-05 [TvP] sKyHigh vs State Orbital Shipyard [10_14].SC2Replay', '16-01-06 [PvZ]BUILD STANDARD.SC2Replay', '16-01-06 [ZvP] STANDARD 1 STARGATE.SC2Replay', '16-01-10 [ZvP] [PRT0SS]Shura vs State Dusk Towers [11_06].SC2Replay', '16-01-11 20_50_57 [PvZ] Prion Terraces.SC2Replay', '16-01-13 [PvZ] State v lIlIlIlIlI [11_02].SC2Replay', '16-01-13 [PvZ] State v llllllllllll [14_33].SC2Replay', '16-01-31 - [PvP] - DT - wickedclownz, HyDE - (V vs D).SC2Replay', '16-02-17 [PvZ] IIIIIIIIIIII v llllllllllll [11_30].SC2Replay', '16-02-17 [PvZ] [STATE]IIIIIIIIIIII vs [ROOT]hydra Ruins of Seras [15_08].SC2Replay', '16-02-17 [ZvP] 万能虚空王 v IIIIIIIIIIII [09_22].SC2Replay', '16-05-10 23_58_23 [ZvT] Frozen Temple.SC2Replay', '16-05-17 08_11_07 [ZvT] Frozen Temple.SC2Replay', '16-07-24 16_20_47 [Perceptor (P) vs [dLife]Aummadour (T)] Galactic Process LE.SC2Replay', '16-12-04 [TvZ] V JJAKJI vs Bly Vaani Research Station.SC2Replay', '16-Bit LE (15) Cyclone rush attempt.SC2Replay', '16-Bit LE (2).SC2Replay']
TooShortReplays = ['16-Bit LE (18).SC2Replay', '16-Bit LE_4.SC2Replay', '17-12-02 18_53_35 [ZvT] (W) 飛蛙 奧德賽 - 天梯版.SC2Replay', "19 - King's Cove LE (3).SC2Replay", '2000 Atmospheres LE (3)_2.SC2Replay', '2000 Atmospheres LE_1.SC2Replay', '2017-12-22_dark_vs_sOs_(Ro16_Dark_vs_sOs_G3).SC2Replay', '2020-01-06 - (P)Jason VS (T)Clem.SC2Replay', '2020-09-15 - (P)talentless VS (Z)KingArthur.SC2Replay', '2020-09-15 - (P)Teshnuburr VS (Z)KingArthur.SC2Replay', '2020-09-15 - (Z)KingArthur VS (P)GGCowabunga.SC2Replay', '2021-02-04 - (T)EXTERMINADOR VS (T)Osiris.SC2Replay', '4r .SC2Replay', 'A.I. 1 (Easy) v Erfeyah - Battle on the Boardwalk LE.SC2Replay', 'A.I. 1 (Easy) v Salvite - Proxima Station LE.SC2Replay', 'A.I. 1 (Easy) v Salvite - Sequencer LE.SC2Replay', 'A.I. 1 (Elite) v Dicliffier - Oxide LE.SC2Replay', 'A.I. 1 (Hard) v JagrsMullets - Ascension to Aiur LE.SC2Replay', 'A.I. 1 (Hard) v prospeKt - Eternal Empire LE_1.SC2Replay', 'A.I. 1 (Hard) v sandboX - Acropolis LE_1.SC2Replay', 'A.I. 1 (Hard) v sandboX - Acropolis LE_2.SC2Replay', 'A.I. 1 (Harder) v Smeeeger - Acropolis LE_10.SC2Replay', 'A.I. 1 (Harder) v Smeeeger - Acropolis LE_11.SC2Replay', 'A.I. 1 (Harder) v Smeeeger - Acropolis LE_2.SC2Replay', 'A.I. 1 (Harder) v Smeeeger - Acropolis LE_6.SC2Replay', 'A.I. 1 (Harder) v Smeeeger - Acropolis LE_7.SC2Replay', 'A.I. 1 (Harder) v Smeeeger - Acropolis LE_9.SC2Replay', 'A.I. 1 (Harder) v Winthrowe - Interloper LE_1.SC2Replay', 'A.I. 1 (Medium) v Erfeyah - Ascension to Aiur LE.SC2Replay', 'A.I. 1 (Medium) v Erfeyah - Blackpink LE.SC2Replay', 'A.I. 1 (Medium) v Erfeyah - Odyssey LE.SC2Replay', 'A.I. 1 (Medium) v sandboX - Acropolis LE_1.SC2Replay', 'A.I. 1 (Medium) v Winthrowe - Odyssey LE_2.SC2Replay', 'A.I. 1 (Very Easy) v CinDra - Abyssal Reef LE.SC2Replay', 'A.I. 1 (Very Easy) v CinDra - Battle on the Boardwalk LE.SC2Replay', 'A.I. 1 (Very Easy) v CinDra - Catalyst LE.SC2Replay', 'A.I. 1 (Very Easy) v CinDra - Neon Violet Square LE_1.SC2Replay', 'A.I. 1 (Very Easy) v Cuervo - Abyssal Reef LE.SC2Replay', 'A.I. 1 (Very Easy) v Cuervo - Abyssal Reef LE_1.SC2Replay', 'A.I. 1 (Very Easy) v Cuervo - Abyssal Reef LE_3.SC2Replay', 'A.I. 1 (Very Easy) v Djorn - Acropolis LE.SC2Replay', 'A.I. 1 (Very Easy) v IvyRex - Catalyst LE.SC2Replay', 'A.I. 1 (Very Easy) v Jettorix - Ascension to Aiur LE.SC2Replay', 'A.I. 1 (Very Easy) v Lambo - Thunderbird LE.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Acropolis LE_12.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Acropolis LE_13.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Acropolis LE_21.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Acropolis LE_25.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Acropolis LE_26.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Acropolis LE_6.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Acropolis LE_8.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Disco Bloodbath LE_5.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Disco Bloodbath LE_6.SC2Replay', 'A.I. 1 (Very Easy) v Mez - Ephemeron LE_1.SC2Replay', "A.I. 1 (Very Easy) v Mez - King's Cove LE_4.SC2Replay", 'A.I. 1 (Very Easy) v Mez - Triton LE_5.SC2Replay', "A.I. 1 (Very Easy) v Mez - Winter's Gate LE_1.SC2Replay", "A.I. 1 (Very Easy) v Mez - Winter's Gate LE_3.SC2Replay", 'A.I. 1 (Very Easy) v Smileblind - Snowbound Colony.SC2Replay', 'A.I. 1 (Very Easy) v WookieMonsta - Acropolis LE.SC2Replay', 'A.I. 1 (Very Hard) v Winthrowe - Ascension to Aiur LE_4.SC2Replay', 'A.I. 1 (Very Hard) v Winthrowe - Ascension to Aiur LE_5.SC2Replay', 'Abiogenesis LE (14)_1.SC2Replay', 'Abiogenesis LE (17)_1.SC2Replay', 'Abiogenesis LE (23)_1.SC2Replay', 'Abiogenesis LE (33).SC2Replay', 'Abiogenesis LE (7)_4.SC2Replay', 'Abyssal Reef LE (11).SC2Replay', 'Abyssal Reef LE (13)_4.SC2Replay', 'Abyssal Reef LE (14)_1.SC2Replay', 'Abyssal Reef LE (2)_1.SC2Replay', 'Abyssal Reef LE (331).SC2Replay', 'Abyssal Reef LE (340)_1.SC2Replay', 'Abyssal Reef LE (4)_1.SC2Replay', 'Abyssal Reef LE (40).SC2Replay', 'Abyssal Reef LE (5)_3.SC2Replay', 'Abyssal Reef LE (8)_2.SC2Replay', 'ACBLACK v DarkTemplar - Cerulean Fall LE.SC2Replay', 'Acid Plant LE (16)_2.SC2Replay', 'Acid Plant LE (2)_7.SC2Replay', 'Acid Plant LE (7)_2.SC2Replay', 'Acid Plant LE (8)_1.SC2Replay', 'Acolyte LE (10).SC2Replay', 'Acolyte LE (3)_2.SC2Replay', 'Acropolis LE (38)_1.SC2Replay', 'Acropolis LE (54).SC2Replay', 'Acropolis LE (70).SC2Replay', 'Acropolis LE (78).SC2Replay', 'AdminA v NoRegreT_ Game 3 - Odyssey LE.SC2Replay', 'Adrenaline v MrFercho - Aura mortal EE.SC2Replay', 'AfreecaDRG v TSGSolar_ Game 3 - Nightshade LE.SC2Replay', 'AgoElazer v soO_ Game 3 - Ever Dream LE.SC2Replay', 'AirOp v Throwfordays - Year Zero LE.SC2Replay', 'Alderon v Throwfordays - Port Aleksander LE.SC2Replay', 'Alkor v Panda - Prüfung von Aiur LE.SC2Replay', 'Allaryce v Harstem_ Game 1 - Abyssal Reef LE.SC2Replay', 'AlphaStarMid_005_TvP.SC2Replay', 'AlphaStarMid_006_PvZ.SC2Replay', 'AlphaStarMid_009_PvP.SC2Replay', 'AlphaStarMid_030_ZvP.SC2Replay', 'AlphaStarMid_031_ZvZ.SC2Replay', 'AlphaStarMid_032_ZvZ.SC2Replay', 'AlphaStarMid_034_PvP.SC2Replay', 'AlphaStarSupervised_003_TvP.SC2Replay', 'AlphaStarSupervised_004_ZvT.SC2Replay', 'AlphaStarSupervised_015_TvT.SC2Replay', 'AlphaStarSupervised_030_PvP.SC2Replay', 'AlphaStar_012_PvZ.SC2Replay', 'alvaro v CinDra - Acid Plant LE.SC2Replay', 'antagomiR v DoUgZ - Ever Dream LE.SC2Replay', 'antagomiR v Dzmitry - Ever Dream LE.SC2Replay', 'antagomiR v EpicLeonel - Eternal Empire LE.SC2Replay', 'antagomiR v EpicLeonel - Nightshade LE.SC2Replay', 'antagomiR v ivanmaldonad - Ever Dream LE.SC2Replay', 'antagomiR v joee - Ever Dream LE.SC2Replay', 'antagomiR v Jonas - Nightshade LE.SC2Replay', 'antagomiR v llllllllllll - Zen LE.SC2Replay', 'antagomiR v llllllllllll - Zen LE_1.SC2Replay', 'antagomiR v Nate - Zen LE.SC2Replay', 'antagomiR v noahneevz - Ever Dream LE.SC2Replay', 'antagomiR v Ottomatic - Ever Dream LE.SC2Replay', 'antagomiR v Railgun - Zen LE.SC2Replay', 'antagomiR v slimespank - Eternal Empire LE.SC2Replay', 'AoretHelloWorld.SC2Replay', 'APMeth v Panda - Odyssee LE.SC2Replay', 'Armani v soO_ Game 2 - 이페머론 - 래더.SC2Replay', 'Ascension to Aiur LE (13)_1.SC2Replay', 'Ascension to Aiur LE (20)_1.SC2Replay', 'Ascension to Aiur LE (21)_1.SC2Replay', 'Ascension to Aiur LE (22)_1.SC2Replay', 'Ascension to Aiur LE (33).SC2Replay', 'Ascension to Aiur LE (40).SC2Replay', 'Ascension to Aiur LE (631).SC2Replay', 'Ascension to Aiur LE_3.SC2Replay', 'Ascension vers Aïur EC (71).SC2Replay', 'Askywarrior v Throwfordays - New Repugnancy LE.SC2Replay', 'Astrea v Denver_ Game 3 - New Repugnancy LE.SC2Replay', 'Astrea v Neeb_ Game 1 - Deathaura LE.SC2Replay', 'Astrea v Scarlett_ Game 3 - Eternal Empire LE.SC2Replay', 'Astrea v Zoun - Romanticide LE_1.SC2Replay', 'AsuraDeath v Throwfordays - Port Aleksander LE.SC2Replay', 'August v Mez - Acropolis LE.SC2Replay', 'Avoš v Motomax - Redshift LE.SC2Replay', "Awers v Harstem_ Game 1 - King's Cove LE.SC2Replay", 'a_3.SC2Replay', 'B2GM - PvP - Platinum 2 - Game 6.SC2Replay', 'B2GM - PvZ - Silver 1 - Game 3.SC2Replay', 'B2GM - TvP - Diamond 2 - Game 24.SC2Replay', 'B2GM - TvT - Diamond 2 - Game 6.SC2Replay', 'B2GM - TvT - Silver 3 - Game 1.SC2Replay', 'B2GM - TvZ - Silver 2 - Game 2.SC2Replay', 'B2GM - ZvT - Diamond 2 - Game 14.SC2Replay', 'B2GM - ZvZ - Silver 1 - Game 1.SC2Replay', 'Backwater LE (26).SC2Replay', 'Backwater LE (4)_5.SC2Replay', 'Backwater LE (8)_2.SC2Replay', 'Backwater LE (9).SC2Replay', 'Badack v prospeKt - Pillars of Gold LE.SC2Replay', 'Bardimus v Throwfordays - Port Aleksander LE.SC2Replay', 'Battle on the Boardwalk LE (6).SC2Replay', "Bedlam v Mez - King's Cove LE.SC2Replay", 'belmont v Throwfordays - Year Zero LE.SC2Replay', 'benjii v Mez - Acropolis LE.SC2Replay', "benttwig v Pono_ Game 1 - Bel'Shir Vestige LE (Void).SC2Replay"]

def ProcessReplay(replayPath):
    data = zp.parse_replay(replayPath, local=True)

    players = data[0]
    timeline = data[1]
    matchInfo = data[3]
    matchMetaData = data[4]

    winnerID = int(matchMetaData["winner"])

    dataPoints = {}
    i = 0
    while (i < len(timeline)):
        p1 = Player(players[1].name, players[1].race, matchInfo, i, timeline, i, 1)
        p2 = Player(players[2].name, players[2].race, matchInfo, i, timeline, i, 2)
        dataPoints[i] = ReplayDataPoint(p1,p2, int(winnerID-1))
        i += 1

    return dataPoints

def SerializeData(replayData, replayName):
        filename = replayName+".jsonData"
        with open(SerializedDataFolder + "/" + filename, "w") as file:
            serializedData = json.dumps(replayData)
            file.write(serializedData)
        print("Saved replay data to file "+filename)
    

def AnalyzeReplays(startIndex, count):
    ReplaysScaned = os.listdir(SerializedDataFolder)
    CorruptedReplays = []
    TooShortReplays = []
    for index in range(len(ReplaysScaned)):
        ReplaysScaned[index] = ReplaysScaned[index].removesuffix("_vectorized.data")
    allFiles = [item for item in os.listdir(ReplaysFolder) if item not in ReplaysScaned]
    for fileIndex in range(startIndex, min(startIndex + count, len(allFiles))):
        filename = allFiles[fileIndex]
        try:
            processedReplay = ProcessReplay(ReplaysFolder+"/"+filename)
            if(len(processedReplay) < 33):
                print("Moving " + filename + " to too short replays folder")
                TooShortReplays.append(filename)
            else:
                VectorizeAndSaveReplay(processedReplay, filename)
        except Exception as e:
            print("Couldn't decode " + filename + " | Moving it to corrupted folder")
            CorruptedReplays.append(filename)
            print(e)
            continue
    
    print(CorruptedReplays)
    print(TooShortReplays)

    for index in range(len(CorruptedReplays)):
        shutil.move(ReplaysFolder+"/"+CorruptedReplays[index],CorruptedReplaysFolder+"/"+CorruptedReplays[index])
    for index in range(len(TooShortReplays)):
        shutil.move(ReplaysFolder+"/"+TooShortReplays[index],TooShortReplaysFolder+"/"+TooShortReplays[index])

def LoadVectorizedData(count, startIndex):
    i = 0
    vectorizedData = []
    allReplays = os.listdir(SerializedDataFolder)
    for fileIndex in range(startIndex, min(startIndex+count,len(allReplays))):
        filename = allReplays[fileIndex]
        if(not filename.__contains__("vectorized")): continue
        with open(SerializedDataFolder + "/" + filename, "r") as file:
            rep =  json.loads(file.read())
            if(len(rep) >= 33):
                vectorizedData.append(rep)
        i += 1
        if(i%100 == 0):
            print("Loaded "+str(i)+"/"+str(len(allReplays)))
        if(i >= count):
            return vectorizedData
    return vectorizedData

def VectorizeAndSaveReplay(replayData, replayName):
    vectorized = []
    i = 0
    while (i < len(replayData)):
        vectorized.append(replayData[i].Vectorize())
        i += 1
    SerializeData(vectorized, replayName+"_vectorized")

t0 = time.time()

threads = []
threadsCount = 6
queueLength = 10
for i in range(threadsCount):
    threads.append(threading.Thread(target=AnalyzeReplays, args=(queueLength*i,queueLength)))
for x in threads:
     x.start()
for x in threads:
     x.join()

t1 = time.time()
print(t1-t0)

#LoadReplays(5000)
#result = LoadVectorizedData(100)

#AnalyzeReplays()
#replays = LoadReplays()
#replays[0]['0'].Vectorize()
#print(replays)