#!/usr/bin/env python3
# Placement-ONLY perfboard diagram (no routed wires →  stays clean).
# ESP32-C3 SuperMini: two pin rows are 6 pitches apart (7 rows incl. both pin rows).
PITCH=46; X0,Y0=120,150; COLS,ROWS=24,10
def X(c): return X0+(c-1)*PITCH
def Y(r): return Y0+(r-1)*PITCH

# component footprints: (name, c1,r1,c2,r2, fill, stroke)
boxes=[
 ('ESP32-C3 SuperMini',2,2,9,8,'#e8eeff','#2d50a8'),   # 8 long x 7 rows (pins row2 & row8)
 ('74HC125 (DIP-14)',12,3,18,6,'#eafaf0','#1a8f3c'),    # 7 x (rows3&6, 0.3in)
 ('MP1584 buck',12,8,15,9,'#fff3e0','#b36b00'),
 ('PC817 (DIP-4)',17,8,18,9,'#fdeef0','#b02a4a'),
]
# used pins: (col,row, label, net-note)
pins=[
 # ESP top row (row2) and bottom row (row8)
 (2,2,'5V','→ +5V bus'),(3,2,'G','→ GND bus'),(5,2,'IO4','→ 74HC125 2A'),(6,2,'IO3','← divider (PWM-ctrl)'),
 (2,8,'IO5','→ 330R→ PC817'),
 # 74HC125 (pins on row3 top / row6 bottom)
 (12,3,'14 Vcc','→ +5V'),(12,6,'1 OE','→ GND'),(13,6,'2 A','← IO4'),(14,6,'1Y','→ 100R→ PWM-mot'),(18,6,'7 G','→ GND'),
 # PC817
 (17,8,'1','← 330R (IO5)'),(17,9,'2','→ GND'),(18,8,'4','→ SW5-a'),(18,9,'3','→ SW5-b'),
 # buck
 (12,8,'24IN+','← +24V(fuse)'),(12,9,'GIN','→ GND'),(15,8,'5OUT','→ +5V bus'),(15,9,'GOUT','→ GND'),
]
# right-edge off-board header
header=[(24,2,'PWM-ctrl'),(24,3,'PWM-mot'),(24,4,'+24V'),(24,5,'GND'),(24,6,'SW5-a'),(24,7,'SW5-b')]
# loose passives placed in free holes: (c,r,text)
passives=[(20,3,'10k ser'),(21,3,'nodeX'),(20,4,'10k'),(22,4,'1uF'),(16,6,'100R'),(16,7,'10k pd'),(4,8,'330R')]

W,Hh=1180,820; o=[]
o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" font-family="Helvetica,Arial,sans-serif">')
o.append(f'<rect width="{W}" height="{Hh}" fill="#fff"/>')
o.append('<text x="590" y="30" text-anchor="middle" font-size="22" font-weight="bold" fill="#111">Heran fan 5 V build - PLACEMENT (7x3 cm, 24x10 holes)</text>')
o.append('<text x="590" y="52" text-anchor="middle" font-size="13" fill="#555">Where each part sits + pin functions. For WIRING see the net list (BUILD_GUIDE 2e) and perfboard_layout.svg.</text>')
o.append('<text x="590" y="70" text-anchor="middle" font-size="12" fill="#a33">ESP32-C3 SuperMini pin rows are 6 holes apart (occupies 7 rows). Verify your module footprint.</text>')
# board + holes
bx,by=X(1)-30,Y(1)-30; bw,bh=(COLS-1)*PITCH+60,(ROWS-1)*PITCH+60
o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="#eef5ef" stroke="#4a7d5a" stroke-width="2"/>')
for c in range(1,COLS+1):
    for r in range(1,ROWS+1): o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="2.6" fill="#b7c9bd"/>')
# power bus hints (rows 1 & 10)
o.append(f'<line x1="{X(1)}" y1="{Y(1)}" x2="{X(24)}" y2="{Y(1)}" stroke="#d11" stroke-width="3"/>')
o.append(f'<text x="{X(1)}" y="{Y(1)-10}" font-size="12" font-weight="bold" fill="#d11">+5 V bus (row 1)</text>')
o.append(f'<line x1="{X(1)}" y1="{Y(10)}" x2="{X(24)}" y2="{Y(10)}" stroke="#111" stroke-width="3"/>')
o.append(f'<text x="{X(1)}" y="{Y(10)+24}" font-size="12" font-weight="bold" fill="#111">GND bus (row 10)</text>')
# boxes
for name,c1,r1,c2,r2,fill,stroke in boxes:
    x1,y1,x2,y2=X(c1)-18,Y(r1)-18,X(c2)+18,Y(r2)+18
    o.append(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="8" fill="{fill}" fill-opacity="0.32" stroke="{stroke}" stroke-width="2.5"/>')
    o.append(f'<text x="{(x1+x2)//2}" y="{y1-8}" text-anchor="middle" font-size="13" font-weight="bold" fill="{stroke}">{name}</text>')
# pins + labels (label sits OUTSIDE/below the dot with halo)
def halo(x,y,txt,col,size=12,anchor='middle',weight='normal'):
    o.append(f'<text x="{int(x)}" y="{int(y)}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" stroke="#fff" stroke-width="4" paint-order="stroke" fill="{col}">{txt}</text>')
for c,r,lab,note in pins:
    x,y=X(c),Y(r)
    o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#333"/>')
    halo(x,y-11,lab,'#0b1020',13,'middle','bold')
    halo(x,y+19,note,'#374151',10)
# header
for c,r,lab in header:
    x,y=X(c),Y(r); o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#555"/>'); halo(x+12,y+4,lab,'#111',11,'start','bold')
o.append(f'<text x="{X(24)}" y="{Y(1)-10}" text-anchor="end" font-size="11" fill="#555">off-board header</text>')
# passives
for c,r,txt in passives:
    x,y=X(c),Y(r); o.append(f'<rect x="{x-20}" y="{y-9}" width="40" height="18" rx="3" fill="#fffbe6" stroke="#b7791f"/>'); halo(x,y+4,txt,'#92400e',9)
# legend / note
o.append(f'<text x="60" y="{Hh-46}" font-size="12" fill="#555">Grey dots = board holes. ESP + buck mount as modules (ESP on female headers). The 74HC125, PC817 and passives sit in the grid.</text>')
o.append(f'<text x="60" y="{Hh-26}" font-size="12" fill="#555">74HC125 is plain HC →  set the buck to ~4.4 V. Arrows on each pin show its connection; exact wiring is the net list in BUILD_GUIDE 2e.</text>')
o.append('</svg>')
open('build/perfboard_placement.svg','w',encoding='utf-8').write('\n'.join(o))
print("placement SVG written:",len('\n'.join(o)),"bytes")
