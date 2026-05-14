---
ctf_name: "2026-DawgCTF"
challenge_name: "Computer Repair II"
category: "osint"
difficulty: "medium"
author: "vestman828"
date: "2026-04-12"
tags: [osint]
---

# Andy Martin

## 문제 설명

> 2026-DawgCTF에 Computer Repair II 문제입니다. Osint입니다.

## 풀이

### 분석

서비스 태그: FZGXPV2에 집중했습니다.
dell 공식 홈페이지에 이 서비스 태그를 입력하고,
제품 사양을 .csv로 다운로드 받았습니다.

구성 요소,부품 번호,설명,수량
"YXW7T : Module,Label,Intel,CI5,Virtual ization Pro,8,Small","56MW5","LBL,INTEL,CI5,VPRO,8,SML","1"
"YFM89 : Module,Placemat,Quick Start Gu ide,LATITUDE,5500,World Wide","91VYG","PLCMT,QSG,LATITUDE,5500,WW","1"
"YCD1H : MOD,ADPT,AC,65W,LTON,7.4,V2,E5","G4X7T","Adapter,Alternating Current,65W,Liteon,7.4,Pwa Integrated,V2,E5","1"
"Y7H78 : Module,Information,Basic Input /Output System,HASH,ENABLE","4P9FX","INFO,HASH,BIOS","1"
"","H82C5","INFO,HASH,ENABLE,VERIFY,RGD","1"
"Y74N9 : Module,Label,GEN2,70MMX110MM,P rint On Demand","0MCWC","LBL,POD,GEN2,CFIG, 70MMX110MM,","1"
"W753G : Module,Information,Direct Ship,Compal,TSINGMA","Y364G","INFO,DIRSHP,CMPL,KUNSHAN","1"
"V2M1P : Module,Information,Royalty,MAX X AUDIO PRO","M3C3H","INFO,RYLTY,WAVES-MAXX,AUD,PRO","1"
"V2C11 : MOD-SRV,WRLES,M.2,9560,NTB","2D1YM","SRV,DRVR,WRLES,BT,9560,NTB","1"
"","D5WCC","SRV,DRVR,WRLES,M.2,9560,NTB","1"
"","V1TMT","SRV,HTML,WRLES,INTEL","1"
.
.
.

이렇게 정리되어 있는 자료를 통해 플래그를 얻었습니다.

### 익스플로잇

```python
(사용한 익스플로잇 없음)
```

## 플래그

```
DawgCTF{15.6IN}
```

## 배운 점

-
