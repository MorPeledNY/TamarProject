;FLAVOR:Marlin
;TIME:189
;Filament used: 0.0756319m
;Layer height: 0.1
;MINX:101.2
;MINY:104.2
;MINZ:0.3
;MAXX:118.8
;MAXY:115.8
;MAXZ:1
;Generated with Cura_SteamEngine 5.2.1
M140 S60
M105
M190 S60
M104 S210
M105
M109 S210
M82 ;absolute extrusion mode
; Ender 3 Custom Start G-code
G92 E0 ; Reset Extruder
G28 ; Home all axes
G1 Z2.0 F3000 ; Move Z Axis up little to prevent scratching of Heat Bed
G1 X0.1 Y20 Z0.3 F5000.0 ; Move to start position

G92 E0 ; Reset Extruder

G1 Z2.0 F3000 ; Move Z Axis up little to prevent scratching of Heat Bed
G1 X5 Y20 Z0.3 F5000.0 ; Move over to prevent blob squish
G92 E0
G92 E0
G1 F2400 E-3
;LAYER_COUNT:8
;LAYER:0
M107
;MESH:2R.stl
G0 F6000 X104.6 Y115.4 Z0.3
;TYPE:WALL-INNER
G1 F2400 E0
G1 F1200 X118.4 Y115.4 E0.68848
G1 X118.4 Y110 E0.95789
G1 X118.4 Y104.6 E1.2273
G1 X104.6 Y104.6 E1.91578
G1 X104.6 Y115.4 E2.4546
G0 F6000 X104.2 Y115.8
;TYPE:WALL-OUTER
G1 F1200 X118.8 Y115.8 E3.18299
G1 X118.8 Y110 E3.47236
G1 X118.8 Y104.2 E3.76172
G1 X104.2 Y104.2 E4.49012
G1 X104.2 Y115.8 E5.06884
G0 F6000 X104.47 Y115.53
G0 X104.7 Y115.04
G0 X104.96 Y115.04
;TYPE:SKIN
G1 F1200 X118.04 Y115.04 E5.72141
G1 X118.04 Y110 E5.97286
G1 X118.04 Y104.96 E6.2243
G1 X104.96 Y104.96 E6.87687
G1 X104.96 Y115.04 E7.37976
G0 F6000 X105.222 Y114.839
G1 F1200 X105.159 Y114.776 E7.3842
G0 F6000 X105.159 Y114.21
G1 F1200 X105.788 Y114.839 E7.42858
G0 F6000 X106.353 Y114.839
G1 F1200 X105.159 Y113.644 E7.51286
G0 F6000 X105.159 Y113.079
G1 F1200 X106.919 Y114.839 E7.63704
G0 F6000 X107.485 Y114.839
G1 F1200 X105.159 Y112.513 E7.80115
G0 F6000 X105.159 Y111.947
G1 F1200 X108.05 Y114.839 E8.00516
G0 F6000 X108.616 Y114.839
G1 F1200 X105.159 Y111.382 E8.24907
G0 F6000 X105.159 Y110.816
G1 F1200 X109.182 Y114.839 E8.53292
G0 F6000 X109.747 Y114.839
G1 F1200 X105.159 Y110.25 E8.85666
G0 F6000 X105.159 Y109.684
G1 F1200 X110.313 Y114.839 E9.22034
G0 F6000 X110.879 Y114.839
G1 F1200 X105.159 Y109.119 E9.62391
G0 F6000 X105.159 Y108.553
G1 F1200 X111.444 Y114.839 E10.06739
G0 F6000 X112.01 Y114.839
G1 F1200 X105.159 Y107.987 E10.5508
G0 F6000 X105.159 Y107.422
G1 F1200 X112.576 Y114.839 E11.07411
G0 F6000 X113.142 Y114.839
G1 F1200 X105.159 Y106.856 E11.63735
G0 F6000 X105.159 Y106.29
G1 F1200 X113.707 Y114.839 E12.2405
G0 F6000 X114.273 Y114.839
G1 F1200 X105.159 Y105.725 E12.88354
G0 F6000 X105.159 Y105.159
G1 F1200 X114.839 Y114.839 E13.56651
G0 F6000 X115.404 Y114.839
G1 F1200 X105.725 Y105.159 E14.24946
G0 F6000 X106.29 Y105.159
G1 F1200 X115.97 Y114.839 E14.93243
G0 F6000 X116.536 Y114.839
G1 F1200 X106.856 Y105.159 E15.61541
G0 F6000 X107.422 Y105.159
G1 F1200 X117.101 Y114.839 E16.29835
G0 F6000 X117.667 Y114.839
G1 F1200 X107.987 Y105.159 E16.98133
G0 F6000 X108.553 Y105.159
G1 F1200 X117.839 Y114.445 E17.6365
G0 F6000 X117.839 Y113.879
G1 F1200 X109.119 Y105.159 E18.25175
G0 F6000 X109.684 Y105.159
G1 F1200 X117.839 Y113.313 E18.82709
G0 F6000 X117.839 Y112.748
G1 F1200 X110.25 Y105.159 E19.36254
G0 F6000 X110.816 Y105.159
G1 F1200 X117.839 Y112.182 E19.85805
G0 F6000 X117.839 Y111.616
G1 F1200 X111.382 Y105.159 E20.31362
G0 F6000 X111.947 Y105.159
G1 F1200 X117.839 Y111.051 E20.72933
G0 F6000 X117.839 Y110.485
G1 F1200 X112.513 Y105.159 E21.10511
G0 F6000 X113.079 Y105.159
G1 F1200 X117.839 Y109.919 E21.44096
G0 F6000 X117.839 Y109.354
G1 F1200 X113.644 Y105.159 E21.73694
G0 F6000 X114.21 Y105.159
G1 F1200 X117.839 Y108.788 E21.99298
G0 F6000 X117.839 Y108.222
G1 F1200 X114.776 Y105.159 E22.20909
G0 F6000 X115.341 Y105.159
G1 F1200 X117.839 Y107.657 E22.38534
G0 F6000 X117.839 Y107.091
G1 F1200 X115.907 Y105.159 E22.52165
G0 F6000 X116.473 Y105.159
G1 F1200 X117.839 Y106.525 E22.61803
G0 F6000 X117.839 Y105.959
G1 F1200 X117.038 Y105.159 E22.67451
G0 F6000 X117.604 Y105.159
G1 F1200 X117.839 Y105.394 E22.69109
;MESH:NONMESH
G0 F300 X117.839 Y105.394 Z0.4
G0 F6000 X118.3 Y105.394
G0 X118.228 Y115.228
G0 X104.6 Y115.4
;TIME_ELAPSED:30.897578
;LAYER:1
M106 S85
;TYPE:WALL-INNER
;MESH:2R.stl
G1 F1350 X118.4 Y115.4 E22.92059
G1 X118.4 Y110 E23.01039
G1 X118.4 Y104.6 E23.10019
G1 X104.6 Y104.6 E23.32969
G1 X104.6 Y115.4 E23.50929
G0 F7500 X104.2 Y115.8
;TYPE:WALL-OUTER
G1 F1350 X118.8 Y115.8 E23.75209
G1 X118.8 Y110 E23.84854
G1 X118.8 Y104.2 E23.945
G1 X104.2 Y104.2 E24.1878
G1 X104.2 Y115.8 E24.38071
G0 F7500 X104.47 Y115.53
G0 X104.7 Y115.04
G0 X104.96 Y115.04
;TYPE:SKIN
G1 F1350 X118.04 Y115.04 E24.59823
G1 X118.04 Y110 E24.68204
G1 X118.04 Y104.96 E24.76586
G1 X104.96 Y104.96 E24.98338
G1 X104.96 Y115.04 E25.15101
G0 F7500 X104.7 Y115.04
G0 X104.7 Y105.274
G0 X105.16 Y105.274
G1 F1350 X105.275 Y105.159 E25.15372
G0 F7500 X105.841 Y105.159
G1 F1350 X105.16 Y105.84 E25.16973
G0 F7500 X105.16 Y106.406
G1 F1350 X106.406 Y105.159 E25.19905
G0 F7500 X106.972 Y105.159
G1 F1350 X105.16 Y106.971 E25.24166
G0 F7500 X105.16 Y107.537
G1 F1350 X107.538 Y105.159 E25.29759
G0 F7500 X108.103 Y105.159
G1 F1350 X105.16 Y108.103 E25.36682
G0 F7500 X105.16 Y108.668
G1 F1350 X108.669 Y105.159 E25.44934
G0 F7500 X109.235 Y105.159
G1 F1350 X105.16 Y109.234 E25.54518
G0 F7500 X105.16 Y109.8
G1 F1350 X109.8 Y105.159 E25.65432
G0 F7500 X110.366 Y105.159
G1 F1350 X105.16 Y110.365 E25.77676
G0 F7500 X105.16 Y110.931
G1 F1350 X110.932 Y105.159 E25.9125
G0 F7500 X111.498 Y105.159
G1 F1350 X105.16 Y111.497 E26.06156
G0 F7500 X105.16 Y112.062
G1 F1350 X112.063 Y105.159 E26.22391
G0 F7500 X112.629 Y105.159
G1 F1350 X105.16 Y112.628 E26.39957
G0 F7500 X105.16 Y113.194
G1 F1350 X113.195 Y105.159 E26.58854
G0 F7500 X113.76 Y105.159
G1 F1350 X105.16 Y113.76 E26.79081
G0 F7500 X105.16 Y114.325
G1 F1350 X114.326 Y105.159 E27.00638
G0 F7500 X114.892 Y105.159
G1 F1350 X105.211 Y114.839 E27.23405
G0 F7500 X105.777 Y114.839
G1 F1350 X115.457 Y105.159 E27.46171
G0 F7500 X116.023 Y105.159
G1 F1350 X106.343 Y114.839 E27.68937
G0 F7500 X106.908 Y114.839
G1 F1350 X116.589 Y105.159 E27.91704
G0 F7500 X117.154 Y105.159
G1 F1350 X107.474 Y114.839 E28.1447
G0 F7500 X108.04 Y114.839
G1 F1350 X117.72 Y105.159 E28.37236
G0 F7500 X117.839 Y105.606
G1 F1350 X108.605 Y114.839 E28.58952
G0 F7500 X109.171 Y114.839
G1 F1350 X117.839 Y106.172 E28.79336
G0 F7500 X117.839 Y106.737
G1 F1350 X109.737 Y114.839 E28.98391
G0 F7500 X110.303 Y114.839
G1 F1350 X117.839 Y107.303 E29.16115
G0 F7500 X117.839 Y107.869
G1 F1350 X110.868 Y114.839 E29.32508
G0 F7500 X111.434 Y114.839
G1 F1350 X117.839 Y108.434 E29.47572
G0 F7500 X117.839 Y109
G1 F1350 X112 Y114.839 E29.61304
G0 F7500 X112.565 Y114.839
G1 F1350 X117.839 Y109.566 E29.73707
G0 F7500 X117.839 Y110.131
G1 F1350 X113.131 Y114.839 E29.84779
G0 F7500 X113.697 Y114.839
G1 F1350 X117.839 Y110.697 E29.9452
G0 F7500 X117.839 Y111.263
G1 F1350 X114.262 Y114.839 E30.02932
G0 F7500 X114.828 Y114.839
G1 F1350 X117.839 Y111.828 E30.10013
G0 F7500 X117.839 Y112.394
G1 F1350 X115.394 Y114.839 E30.15763
G0 F7500 X115.959 Y114.839
G1 F1350 X117.839 Y112.96 E30.20184
G0 F7500 X117.839 Y113.525
G1 F1350 X116.525 Y114.839 E30.23274
G0 F7500 X117.091 Y114.839
G1 F1350 X117.839 Y114.091 E30.25033
G0 F7500 X117.839 Y114.657
G1 F1350 X117.656 Y114.839 E30.25463
;MESH:NONMESH
G0 F300 X117.656 Y114.839 Z0.5
G0 F7500 X117.656 Y115.3
G0 X104.6 Y115.4
;TIME_ELAPSED:55.183711
;LAYER:2
M106 S170
;TYPE:WALL-INNER
;MESH:2R.stl
G1 F1500 X118.4 Y115.4 E30.48412
G1 X118.4 Y110 E30.57392
G1 X118.4 Y104.6 E30.66372
G1 X104.6 Y104.6 E30.89322
G1 X104.6 Y115.4 E31.07282
G0 F9000 X104.2 Y115.8
;TYPE:WALL-OUTER
G1 F1500 X118.8 Y115.8 E31.31562
G1 X118.8 Y110 E31.41208
G1 X118.8 Y104.2 E31.50853
G1 X104.2 Y104.2 E31.75133
G1 X104.2 Y115.8 E31.94424
G0 F9000 X104.47 Y115.53
G0 X104.7 Y115.04
G0 X104.96 Y115.04
;TYPE:SKIN
G1 F1500 X118.04 Y115.04 E32.16176
G1 X118.04 Y110 E32.24558
G1 X118.04 Y104.96 E32.32939
G1 X104.96 Y104.96 E32.54691
G1 X104.96 Y115.04 E32.71454
G0 F9000 X105.222 Y114.839
G1 F1500 X105.159 Y114.776 E32.71603
G0 F9000 X105.159 Y114.21
G1 F1500 X105.788 Y114.839 E32.73082
G0 F9000 X106.353 Y114.839
G1 F1500 X105.159 Y113.644 E32.75891
G0 F9000 X105.159 Y113.079
G1 F1500 X106.919 Y114.839 E32.8003
G0 F9000 X107.485 Y114.839
G1 F1500 X105.159 Y112.513 E32.85501
G0 F9000 X105.159 Y111.947
G1 F1500 X108.05 Y114.839 E32.92301
G0 F9000 X108.616 Y114.839
G1 F1500 X105.159 Y111.382 E33.00432
G0 F9000 X105.159 Y110.816
G1 F1500 X109.182 Y114.839 E33.09893
G0 F9000 X109.747 Y114.839
G1 F1500 X105.159 Y110.25 E33.20684
G0 F9000 X105.159 Y109.684
G1 F1500 X110.313 Y114.839 E33.32807
G0 F9000 X110.879 Y114.839
G1 F1500 X105.159 Y109.119 E33.4626
G0 F9000 X105.159 Y108.553
G1 F1500 X111.444 Y114.839 E33.61042
G0 F9000 X112.01 Y114.839
G1 F1500 X105.159 Y107.987 E33.77156
G0 F9000 X105.159 Y107.422
G1 F1500 X112.576 Y114.839 E33.946
G0 F9000 X113.142 Y114.839
G1 F1500 X105.159 Y106.856 E34.13374
G0 F9000 X105.159 Y106.29
G1 F1500 X113.707 Y114.839 E34.33479
G0 F9000 X114.273 Y114.839
G1 F1500 X105.159 Y105.725 E34.54914
G0 F9000 X105.159 Y105.159
G1 F1500 X114.839 Y114.839 E34.7768
G0 F9000 X115.404 Y114.839
G1 F1500 X105.725 Y105.159 E35.00444
G0 F9000 X106.29 Y105.159
G1 F1500 X115.97 Y114.839 E35.2321
G0 F9000 X116.536 Y114.839
G1 F1500 X106.856 Y105.159 E35.45976
G0 F9000 X107.422 Y105.159
G1 F1500 X117.101 Y114.839 E35.68741
G0 F9000 X117.667 Y114.839
G1 F1500 X107.987 Y105.159 E35.91507
G0 F9000 X108.553 Y105.159
G1 F1500 X117.839 Y114.445 E36.13346
G0 F9000 X117.839 Y113.879
G1 F1500 X109.119 Y105.159 E36.33854
G0 F9000 X109.684 Y105.159
G1 F1500 X117.839 Y113.313 E36.53032
G0 F9000 X117.839 Y112.748
G1 F1500 X110.25 Y105.159 E36.7088
G0 F9000 X110.816 Y105.159
G1 F1500 X117.839 Y112.182 E36.87397
G0 F9000 X117.839 Y111.616
G1 F1500 X111.382 Y105.159 E37.02583
G0 F9000 X111.947 Y105.159
G1 F1500 X117.839 Y111.051 E37.1644
G0 F9000 X117.839 Y110.485
G1 F1500 X112.513 Y105.159 E37.28966
G0 F9000 X113.079 Y105.159
G1 F1500 X117.839 Y109.919 E37.40161
G0 F9000 X117.839 Y109.354
G1 F1500 X113.644 Y105.159 E37.50027
G0 F9000 X114.21 Y105.159
G1 F1500 X117.839 Y108.788 E37.58562
G0 F9000 X117.839 Y108.222
G1 F1500 X114.776 Y105.159 E37.65766
G0 F9000 X115.341 Y105.159
G1 F1500 X117.839 Y107.657 E37.71641
G0 F9000 X117.839 Y107.091
G1 F1500 X115.907 Y105.159 E37.76184
G0 F9000 X116.473 Y105.159
G1 F1500 X117.839 Y106.525 E37.79397
G0 F9000 X117.839 Y105.959
G1 F1500 X117.038 Y105.159 E37.8128
G0 F9000 X117.604 Y105.159
G1 F1500 X117.839 Y105.394 E37.81832
;MESH:NONMESH
G0 F300 X117.839 Y105.394 Z0.6
G0 F9000 X118.3 Y105.394
G0 X118.228 Y115.228
G0 X115.4 Y115.4
;TIME_ELAPSED:77.498274
;LAYER:3
M106 S255
;TYPE:WALL-INNER
;MESH:2R.stl
G1 F1500 X115.4 Y110 E37.90812
G1 X115.4 Y104.6 E37.99793
G1 X101.6 Y104.6 E38.22742
G1 X101.6 Y115.4 E38.40703
G1 X115.4 Y115.4 E38.63652
G0 F9000 X115.8 Y115.8
;TYPE:WALL-OUTER
G1 F1500 X115.8 Y110 E38.73298
G1 X115.8 Y104.2 E38.82943
G1 X101.2 Y104.2 E39.07223
G1 X101.2 Y115.8 E39.26514
G1 X115.8 Y115.8 E39.50794
G0 F9000 X115.53 Y115.53
G0 X115.3 Y115.04
G0 X115.04 Y115.04
;TYPE:SKIN
G1 F1500 X115.04 Y104.96 E39.67557
G1 X101.96 Y104.96 E39.89309
G1 X101.96 Y110 E39.97691
G1 X101.96 Y115.04 E40.06072
G1 X115.04 Y115.04 E40.27824
G0 F9000 X114.839 Y114.263
G1 F1500 X114.262 Y114.839 E40.2918
G0 F9000 X113.697 Y114.839
G1 F1500 X114.839 Y113.697 E40.31866
G0 F9000 X114.839 Y113.132
G1 F1500 X113.131 Y114.839 E40.35882
G0 F9000 X112.565 Y114.839
G1 F1500 X114.839 Y112.566 E40.41229
G0 F9000 X114.839 Y112
G1 F1500 X112 Y114.839 E40.47905
G0 F9000 X111.434 Y114.839
G1 F1500 X114.839 Y111.435 E40.55912
G0 F9000 X114.839 Y110.869
G1 F1500 X110.868 Y114.839 E40.6525
G0 F9000 X110.303 Y114.839
G1 F1500 X114.839 Y110.303 E40.75918
G0 F9000 X114.839 Y109.738
G1 F1500 X109.737 Y114.839 E40.87916
G0 F9000 X109.171 Y114.839
G1 F1500 X114.839 Y109.172 E41.01245
G0 F9000 X114.839 Y108.606
G1 F1500 X108.605 Y114.839 E41.15906
G0 F9000 X108.04 Y114.839
G1 F1500 X114.839 Y108.04 E41.31896
G0 F9000 X114.839 Y107.475
G1 F1500 X107.474 Y114.839 E41.49216
G0 F9000 X106.908 Y114.839
G1 F1500 X114.839 Y106.909 E41.67867
G0 F9000 X114.839 Y106.343
G1 F1500 X106.343 Y114.839 E41.87849
G0 F9000 X105.777 Y114.839
G1 F1500 X114.839 Y105.778 E42.0916
G0 F9000 X114.839 Y105.212
G1 F1500 X105.211 Y114.839 E42.31802
G0 F9000 X104.646 Y114.839
G1 F1500 X114.326 Y105.159 E42.54568
G0 F9000 X113.76 Y105.159
G1 F1500 X104.08 Y114.839 E42.77334
G0 F9000 X103.514 Y114.839
G1 F1500 X113.195 Y105.159 E43.00101
G0 F9000 X112.629 Y105.159
G1 F1500 X102.949 Y114.839 E43.22867
G0 F9000 X102.383 Y114.839
G1 F1500 X112.063 Y105.159 E43.45633
G0 F9000 X111.498 Y105.159
G1 F1500 X102.159 Y114.497 E43.67595
G0 F9000 X102.159 Y113.931
G1 F1500 X110.932 Y105.159 E43.88227
G0 F9000 X110.366 Y105.159
G1 F1500 X102.159 Y113.366 E44.07529
G0 F9000 X102.159 Y112.8
G1 F1500 X109.8 Y105.159 E44.25499
G0 F9000 X109.235 Y105.159
G1 F1500 X102.159 Y112.234 E44.4214
G0 F9000 X102.159 Y111.669
G1 F1500 X108.669 Y105.159 E44.5745
G0 F9000 X108.103 Y105.159
G1 F1500 X102.159 Y111.103 E44.7143
G0 F9000 X102.159 Y110.537
G1 F1500 X107.538 Y105.159 E44.84079
G0 F9000 X106.972 Y105.159
G1 F1500 X102.159 Y109.972 E44.95398
G0 F9000 X102.159 Y109.406
G1 F1500 X106.406 Y105.159 E45.05387
G0 F9000 X105.841 Y105.159
G1 F1500 X102.159 Y108.84 E45.14045
G0 F9000 X102.159 Y108.275
G1 F1500 X105.275 Y105.159 E45.21373
G0 F9000 X104.709 Y105.159
G1 F1500 X102.159 Y107.709 E45.27371
G0 F9000 X102.159 Y107.143
G1 F1500 X104.144 Y105.159 E45.32038
G0 F9000 X103.578 Y105.159
G1 F1500 X102.159 Y106.577 E45.35374
G0 F9000 X102.159 Y106.012
G1 F1500 X103.012 Y105.159 E45.3738
G0 F9000 X102.447 Y105.159
G1 F1500 X102.159 Y105.446 E45.38056
;MESH:NONMESH
G0 F300 X102.159 Y105.446 Z0.7
G0 F9000 X101.7 Y105.446
G0 X101.772 Y115.228
G0 X115.4 Y115.4
