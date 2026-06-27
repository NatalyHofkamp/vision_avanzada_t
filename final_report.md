
# Final report: EGNN_delta_soft_mask_biological con validación separada

## Resumen del experimento

Se evaluó `EGNN_delta_soft_mask_biological` con separación train/validation/test. Los hiperparámetros se seleccionaron usando `validation_rmsd_global_mean` y los resultados finales se reportan en test.

**Respuesta directa:** No: soft-mask no supera al copy baseline en RMSD medio de test.

## Configuración usada

- QUICK_RUN: True
- FULL_RUN: False
- USE_OPTUNA: True
- Backend de la mejor configuración: optuna
- Optuna disponible: True
- Mejor validación Optuna: 9.962
- Mejor validación grid referencia: 9.991
- Optuna mejor que grid: True
- EPOCHS finales: 8
- SEARCH_EPOCHS: 4
- Trials/configuraciones evaluadas: 22
- Folds usados para búsqueda: 2
- Folds de test: 6

## Mejores hiperparámetros

| outside_region_scale | w_static | w_region | w_dist | w_local | learning_rate | validation_rmsd_global_mean | search_backend |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.027 | 8.796 | 6.410 | 3.686 | 0.593 | 0.004 | 9.962 | optuna |

## Métricas finales en test

- Copy baseline RMSD medio: 9.641 A.
- Soft-mask RMSD medio: 9.744 A.
- Mejora soft vs copy: -1.070%.
- Casos soft mejores que copy: 63.043%.
- Mejora soft vs masked estricto: 0.246%.
- Mejora soft vs delta biológico anterior: -0.658%.
- Cambio soft vs interpolación oracle: -102.141%.

## Tabla comparativa principal

| method | rmsd_global_mean | mae_coords_mean | distance_matrix_error_mean | improvement_vs_copy_pct_mean | closer_than_inactive_pct | n |
| --- | --- | --- | --- | --- | --- | --- |
| EGNN_delta_masked_biological | 9.768 | 4.280 | 4.995 | -3.132 | 61.957 | 92.000 |
| EGNN_delta_soft_mask_biological | 9.744 | 4.265 | 5.046 | -3.353 | 63.043 | 92.000 |
| copy_inactive | 9.641 | 4.185 | 4.758 | 0.000 | 0.000 | 92.000 |
| egnn_delta_bio_guided | 9.681 | 4.213 | 4.886 | -2.091 | 69.565 | 92.000 |
| linear_interp_0.50 | 4.821 | 2.092 | 2.653 | 50.000 | 98.913 | 92.000 |
| previous_egnn_reported | 11.002 | 4.921 | 6.329 | NA | NA | 6.000 |

## Resultados de búsqueda

| validation_rmsd_global_mean | outside_region_scale | w_static | w_region | w_dist | w_local | learning_rate | search_backend |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9.962 | 0.027 | 8.796 | 6.410 | 3.686 | 0.593 | 0.004 | optuna |
| 9.991 | 0.200 | 2.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.027 | 0.050 | 5.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.032 | 0.100 | 2.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.045 | 0.010 | 5.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.063 | 0.050 | 10.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.064 | 0.010 | 10.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.076 | 0.200 | 5.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.090 | 0.100 | 10.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.090 | 0.169 | 2.664 | 9.726 | 3.988 | 4.728 | 0.003 | optuna |
| 10.094 | 0.010 | 2.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.107 | 0.098 | 1.879 | 7.158 | 2.481 | 1.049 | 0.000 | optuna |
| 10.128 | 0.135 | 3.621 | 6.507 | 1.128 | 1.815 | 0.000 | optuna |
| 10.129 | 0.100 | 5.000 | 5.000 | 2.000 | 2.000 | 0.000 | reference_grid |
| 10.131 | 0.251 | 2.911 | 2.636 | 1.325 | 1.869 | 0.000 | optuna |

## Validación estadística

Diferencia positiva = el baseline tiene mayor RMSD que soft-mask, por lo tanto soft-mask mejora.

| baseline_method | target_method | n_pairs | mean_rmsd_diff_baseline_minus_soft | std_diff | ci95_low | ci95_high | wilcoxon_p | paired_ttest_p | soft_better_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| copy_inactive | EGNN_delta_soft_mask_biological | 92.000 | -0.103 | 0.791 | -0.265 | 0.058 | 0.099 | 0.214 | 0.000 |
| egnn_delta_bio_guided | EGNN_delta_soft_mask_biological | 92.000 | -0.064 | 0.484 | -0.163 | 0.035 | 0.184 | 0.210 | 0.000 |
| EGNN_delta_masked_biological | EGNN_delta_soft_mask_biological | 92.000 | 0.024 | 0.176 | -0.012 | 0.060 | 0.005 | 0.193 | 1.000 |

Contra copy: diferencia media=-0.103 A, CI95=[-0.265, 0.058]. La comparación contra copy no es estadísticamente significativa al 5% usando el menor p-value disponible (p=0.099).

## Análisis con y sin ABL1

| subset | method | rmsd_global_mean | improvement_vs_copy_pct_mean | closer_than_inactive_pct | n |
| --- | --- | --- | --- | --- | --- |
| ABL1 | EGNN_delta_masked_biological | 7.410 | -17.216 | 22.222 | 18.000 |
| ABL1 | EGNN_delta_soft_mask_biological | 7.541 | -18.937 | 16.667 | 18.000 |
| ABL1 | copy_inactive | 6.324 | 0.000 | 0.000 | 18.000 |
| ABL1 | egnn_delta_bio_guided | 6.713 | -5.686 | 22.222 | 18.000 |
| sin_ABL1 | EGNN_delta_masked_biological | 10.342 | 0.104 | 71.622 | 74.000 |
| sin_ABL1 | EGNN_delta_soft_mask_biological | 10.280 | 0.227 | 74.324 | 74.000 |
| sin_ABL1 | copy_inactive | 10.448 | 0.000 | 0.000 | 74.000 |
| sin_ABL1 | egnn_delta_bio_guided | 10.403 | -1.265 | 81.081 | 74.000 |
| todos | EGNN_delta_masked_biological | 9.768 | -3.132 | 61.957 | 92.000 |
| todos | EGNN_delta_soft_mask_biological | 9.744 | -3.353 | 63.043 | 92.000 |
| todos | copy_inactive | 9.641 | 0.000 | 0.000 | 92.000 |
| todos | egnn_delta_bio_guided | 9.681 | -2.091 | 69.565 | 92.000 |

ABL1 RMSD soft=7.541 A; sin ABL1 RMSD soft=10.280 A.

## Análisis por quinasa

### Quinasas donde soft mejora vs copy

| kinase | soft_improvement_vs_copy_pct | soft_improvement_vs_masked_pct | soft_improvement_vs_old_delta_pct | soft_rmsd | copy_rmsd | masked_rmsd | old_delta_rmsd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KIT | 4.432 | 1.691 | 1.278 | 9.582 | 10.027 | 9.747 | 9.706 |
| PDGFRA | 4.247 | 1.084 | -0.691 | 10.010 | 10.454 | 10.120 | 9.941 |
| EGFR | 1.813 | 0.413 | -0.005 | 11.252 | 11.460 | 11.299 | 11.252 |
| FGFR1 | 1.766 | 0.691 | 0.312 | 12.908 | 13.140 | 12.998 | 12.948 |

### Quinasas donde soft empeora o empata vs copy

| kinase | soft_improvement_vs_copy_pct | soft_improvement_vs_masked_pct | soft_improvement_vs_old_delta_pct | soft_rmsd | copy_rmsd | masked_rmsd | old_delta_rmsd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ABL1 | -19.245 | -1.769 | -12.336 | 7.541 | 6.324 | 7.410 | 6.713 |
| BRAF | -3.417 | -0.772 | 4.609 | 7.385 | 7.141 | 7.329 | 7.742 |

## Análisis por región funcional

### Regiones con mejor RMSD soft

| region | rmsd_region | n |
| --- | --- | --- |
| hrd | 8.156 | 92.000 |
| alphac | 8.983 | 92.000 |
| atp_binding | 9.258 | 92.000 |

### Regiones más difíciles

| region | rmsd_region | n |
| --- | --- | --- |
| activation_loop | 11.679 | 92.000 |
| dfg | 9.397 | 92.000 |
| atp_binding | 9.258 | 92.000 |

## Gráficos principales

Los gráficos detallados se muestran directamente dentro del notebook y no se guardan como archivos.

### RMSD medio por método en test

```text
EGNN_delta_masked_biological       | ######################### 9.768
EGNN_delta_soft_mask_biological    | ######################### 9.744
copy_inactive                      | ######################### 9.641
egnn_delta_bio_guided              | ######################### 9.681
linear_interp_0.50                 | ############ 4.821
previous_egnn_reported             | ############################ 11.002
```

### Mejora vs copy por método en test

```text
EGNN_delta_masked_biological       | ## -3.132
EGNN_delta_soft_mask_biological    | ## -3.353
copy_inactive                      | # 0.000
egnn_delta_bio_guided              | # -2.091
linear_interp_0.50                 | ############################ 50.000
```

## Conclusiones automáticas

- Soft-mask vs copy en test: No: soft-mask no supera al copy baseline en RMSD medio de test.
- Significancia vs copy: La comparación contra copy no es estadísticamente significativa al 5% usando el menor p-value disponible (p=0.099).
- Optuna/fallback: Optuna encontró mejor validación que el grid de referencia (9.962 vs 9.991).
- ABL1: ABL1 RMSD soft=7.541 A; sin ABL1 RMSD soft=10.280 A.
- Mejora sin ABL1: revisar la tabla `sin_ABL1`; si mantiene mejora positiva, el problema principal está concentrado en kinases específicas.
- Recomendación: seguir optimizando datos/alineamiento. Si la mejora sigue siendo marginal o no significativa, conviene priorizar alineamiento, pares y anotaciones funcionales antes de aumentar complejidad arquitectónica.

## Limitaciones

- El split de validación se construye dentro de cada fold con datos disponibles; en QUICK_RUN usa menos folds para búsqueda.
- Las regiones funcionales siguen siendo proxies cuando no hay anotaciones residuo-a-residuo curadas.
- El fallback PDB alinea por orden de CA y no por KLIFS residue numbering ni alineamiento estructural robusto.
- El guidance activo/inactivo es un clasificador proxy con features geométricas simples.
- Optuna puede sobreajustar la validación si hay pocos pares; confirmar con FULL_RUN.
- La verificación DFG/alphaC del notebook 05 mide sobre coordenadas CA generadas. Aunque el pipeline actualizado puede usar `pocket` y `klifs_to_ca_index` para ubicar el motivo DFG con mayor precisión, no evalúa átomos de cadena lateral, rotámeros ni distancias catalíticas completas.
- Si los artefactos disponibles fueron generados antes de propagar `pocket`, `klifs_residue_map` y `klifs_to_ca_index`, el notebook 05 usa una aproximación basada en el PDB inactivo y reporta el nivel de mapeo en `mapping_status`. Las muestras sin mapeo quedan como `unmapped`.
- La región alphaC se trata como una ventana geométrica/proxy salvo que el dataset incluya una definición explícita de las posiciones KLIFS usadas para alphaC-in. Por eso la etiqueta DFG/alphaC debe interpretarse como criterio geométrico operativo, no como anotación estructural completa.
- Designability evalúa consistencia física aproximada de una geometría con una secuencia diseñada y re-plegada. No demuestra actividad biológica real ni que esa conformación exista necesariamente en la naturaleza.
- Si `ProteinMPNN` o `esm`/ESMFold no están disponibles, el notebook 05 guarda la verificación como `skipped` en el CSV en vez de simular resultados.
- Si no existen checkpoints en `checkpoints/egnn_loko`, el notebook 05 no re-entrena la EGNN. Puede usar coordenadas ya generadas por `04` como fallback de solo lectura, y lo marca explícitamente en la columna `source`.

## Próximos pasos

- Ejecutar `FULL_RUN=True` con más trials de Optuna.
- Separar validación/test por quinasa y repetir con semillas diferentes.
- Mejorar alineamiento de residuos antes de definir deltas.
- Reemplazar proxies por anotaciones KLIFS de DFG, alphaC, HRD y ATP-binding.
- Si los datos/alineamientos mejoran y la señal persiste, recién entonces probar cambios arquitectónicos más grandes.
