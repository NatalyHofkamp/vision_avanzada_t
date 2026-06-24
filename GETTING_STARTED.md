# Getting Started: Step-by-Step Guide

## 🎯 Objetivo

Después de leer esto, serás capaz de:
- ✅ Entrenar modelos EGNN y guardarlos automáticamente
- ✅ Recargar modelos sin re-entrenar (15-20x más rápido)
- ✅ Hacer análisis completo después de reiniciar el kernel
- ✅ Usar modelos para predicciones en datos nuevos

**Tiempo total:** ~3 horas (primera vez) o ~5 minutos (después)

---

## 📋 Pre-requisitos

Verifica que tienes:
- [ ] Jupyter Notebook abierto con `04_egnn_generate_active.ipynb`
- [ ] PyTorch instalado (`torch.cuda.is_available()` → True o False)
- [ ] Dataset: `dataset_ready.pkl` en el mismo directorio
- [ ] LOKO folds: carpeta `data/loko_folds/` con archivos `fold_*.pkl`

---

## 🚀 Workflow A: Entrenar Modelos por Primera Vez

### Paso 1: Verificar Setup (5 minutos)

Ejecuta **Sección 1** (Imports):
```
✓ Device: cuda o cpu
✓ PyTorch version: x.x.x
✓ Epochs: 50 | Batch size: 1 | LR: 1e-4
```

Si ves estos mensajes, ¡estamos listos!

### Paso 2: Cargar y Explorar Dataset (10 minutos)

Ejecuta **Secciones 2 y 3**:
```
✓ Dataset aplanado: 1234 muestras (dicts)
✓ Dataset class + collate: OK
```

### Paso 3: Definir Modelo y Funciones (5 minutos)

Ejecuta **Secciones 4 y 5**:
```
✓ SimpleEGNN model defined
✓ Funciones de loss, métricas, train_epoch y validate definidas
```

### Paso 4: Cargar LOKO Folds (2 minutos)

Ejecuta **Sección 6**:
```
✓ Loaded 5 LOKO folds
✓ Prepared 5 LOKO folds
```

### Paso 5: **ENTRENAR** (30 min - 2 horas)

Ejecuta **Sección 7** (el loop de entrenamiento):

**Durante el entrenamiento, verás:**
```
=== Fold fold_0 | test kinase: ABL1 ===
  Epoch 1/50: train_loss=0.2345, val_loss=0.2456
  Epoch 10/50: train_loss=0.1234, val_loss=0.1345
  ...
  Epoch 50/50: train_loss=0.0456, val_loss=0.0534
  ✓ Training finished
  Test metrics:
    RMSD: 0.8234 Å | MAE: 0.5123 Å | ...
  ✓ Checkpoint saved: checkpoints/egnn_loko/fold_0.pt    ← 🎉 KEY!

=== Fold fold_1 | test kinase: FGFR1 ===
  ...
  ✓ Checkpoint saved: checkpoints/egnn_loko/fold_1.pt    ← 🎉 SAVED!
  
... (más folds)

=== LOKO training complete ===
✓ Results summary saved: checkpoints/egnn_loko/all_results_summary.pkl
```

**¿Qué pasó?** ✅ Modelos guardados a disco en `checkpoints/egnn_loko/`

### Paso 6: Resumen Científico (1 minuto)

Ejecuta **Sección 8**:
```
SCIENTIFIC SUMMARY
  Total samples: 1234
  Unique kinases: 5
  RMSD (Å): 0.8234 ± 0.0567
  MAE (Å): 0.5123 ± 0.0345
  ...
  ✓ Analysis complete!
```

### Paso 7: Test de Equivariancia (2 minutos)

Ejecuta **Sección 9**:
```
ROTATIONAL EQUIVARIANCE TEST
✓ Using models from results_per_fold (Sección 7 training session)
✓ fold_0 (ABL1): equivariante (max_diff=3.45e-04)
✓ fold_1 (FGFR1): equivariante (max_diff=2.12e-04)
...
✓ Equivariant models: 5/5
✓ Source: FROM TRAINING SESSION (Sección 7)
```

### 🎉 ¡Entrenamiento Completado!

**Verificación:**
```bash
ls -lh checkpoints/egnn_loko/
# Output:
# fold_0.pt (~15 MB)
# fold_1.pt (~12 MB)
# ...
# all_results_summary.pkl (~50 KB)
```

---

## 🔄 Workflow B: Después de Reiniciar Kernel (RECOMENDADO)

**Scenario:** Cerraste Jupyter, la reabriste. Quieres rápidamente analizar los resultados sin re-entrenar.

### Paso 1: Ejecutar Setup (2 minutos)

Ejecuta **Secciones 1 - 5** (una por una):
- Sección 1: Imports
- Sección 2: Load dataset
- Sección 3: Dataset class
- Sección 4: Model definition
- Sección 5: Loss functions

**Cada una debe mostrar ✓ OK**

**No ejecutes Sección 6 (no necesitaremos LOKO folds todavía)**

### Paso 2: **Recargar Modelos** (10 segundos)

Ejecuta **Sección 10**:

```
================================================================================
SECTION 11: RELOAD TRAINED MODELS FROM CHECKPOINTS
================================================================================

Found 5 checkpoint(s). Loading...

✓ fold_0 (ABL1): loaded successfully
✓ fold_1 (FGFR1): loaded successfully
✓ fold_2 (SRC): loaded successfully
✓ fold_3 (MEK1): loaded successfully
✓ fold_4 (RAF1): loaded successfully

================================================================================
RELOADED MODELS SUMMARY
================================================================================

fold    test_kinase  rmsd     mae      dist_err  recovery  best_val_loss
fold_0  ABL1         0.8234   0.5123   1.2345    78.50     0.0456
fold_1  FGFR1        0.7891   0.4956   1.1203    81.23     0.0392
fold_2  SRC          0.8567   0.5341   1.3456    75.80     0.0498
fold_3  MEK1         0.7654   0.4789   1.0987    82.10     0.0378
fold_4  RAF1         0.9123   0.5678   1.4567    72.45     0.0521

✓ 5 models successfully reloaded
✓ Ready for use in Sección 9 (equivariance test) or further analysis
```

**¿Qué pasó?** ✅ Todos los modelos cargados desde checkpoints (sin re-entrenar!)

### Paso 3: Test de Equivariancia (2 minutos)

Ejecuta **Sección 9**:

```
================================================================================
ROTATIONAL EQUIVARIANCE TEST
================================================================================

✓ Using models from loaded_models (Sección 10)

✓ fold_0 (ABL1): equivariante (max_diff=3.45e-04)
✓ fold_1 (FGFR1): equivariante (max_diff=2.12e-04)
✓ fold_2 (SRC): equivariante (max_diff=1.89e-04)

================================================================================
EQUIVARIANCE SUMMARY TABLE
================================================================================

fold    kinase   max_diff     mean_rel_error  equivariant_ok
fold_0  ABL1     3.45e-04     1.23e-05        True
fold_1  FGFR1    2.12e-04     8.90e-06        True
fold_2  SRC      1.89e-04     7.34e-06        True

✓ Equivariant models: 3/3
✓ Source: LOADED FROM CHECKPOINTS (Sección 10)
```

**¿Qué pasó?** ✅ Test usando modelos reloaded (NO re-entrenados!)

### Paso 4: Análisis Personalizado (opcional, 5-30 min)

Ejecuta **Sección 11** para utilities de batch inference:

```python
# Puedes usar loaded_models para tus propios análisis:
model = loaded_models['fold_0']['model']
test_metrics = loaded_models['fold_0']['test_metrics']

# Hacer predicciones en datos nuevos, visualizaciones, etc.
```

### 🎉 ¡Análisis Completado en ~5 Minutos!

**Sin re-entrenar. 15-20x más rápido.**

---

## 📊 Comparación de Tiempos

```
Workflow A (Primera Vez):
  Secciones 1-5:     ~15 min  [Setup]
  Sección 7:         ~1-2 h   [TRAINING] ← Principal
  Secciones 8-9:     ~3 min   [Análisis]
  ━━━━━━━━━━━━━━━━━━━━━━━━━
  TOTAL:             ~1.5-2.5 horas

Workflow B (Después de Restart):
  Secciones 1-5:     ~2 min   [Setup]
  Sección 10:        ~10 seg  [RELOAD]  ← Muy rápido!
  Sección 9:         ~2 min   [Análisis]
  ━━━━━━━━━━━━━━━━━━━━━━━━━
  TOTAL:             ~5 minutos ⚡ (30x más rápido)
```

---

## 🔍 ¿Cómo Verifico que todo Funciona?

### Verificación 1: Checkpoints Guardados

```bash
# En terminal, en el mismo directorio que el notebook:
ls -lh checkpoints/egnn_loko/

# Esperado:
# fold_0.pt (10-20 MB)
# fold_1.pt (10-20 MB)
# ...
# all_results_summary.pkl
```

### Verificación 2: Modelos Recargados

En el notebook, después de Sección 10:

```python
# Deberías poder hacer esto:
print(loaded_models.keys())
# Output: dict_keys(['fold_0', 'fold_1', 'fold_2', ...])

# Y acceder a modelos:
model = loaded_models['fold_0']['model']
print(type(model))
# Output: <class '__main__.SimpleEGNN'>

# Y métricas:
print(loaded_models['fold_0']['test_metrics'])
# Output: {'rmsd': 0.8234, 'mae': 0.5123, ...}
```

### Verificación 3: Equivariancia Correcta

En el notebook, después de Sección 9:

```python
# Deberías ver esto:
print(equiv_df)
# Output: Tabla con todas las filas "equivariant_ok = True"
```

Si ves:
- ✅ Checkpoints files en `checkpoints/egnn_loko/`
- ✅ `loaded_models` dict con N modelos
- ✅ Sección 9 mostrando "LOADED FROM CHECKPOINTS"
- ✅ Todos los modelos equivariantes

**¡Estás listo!** 🎉

---

## ⚠️ Problemas Comunes y Soluciones

### Problema 1: "No checkpoint files found in checkpoints/egnn_loko"

**¿Por qué?** No ejecutaste Sección 7 (training).

**Solución:**
```
1. Ejecuta Secciones 1-6 (setup)
2. Ejecuta Sección 7 (training)  ← Esto crea los checkpoints
3. Luego ejecuta Sección 10 (reload)
```

### Problema 2: "NameError: name 'results_per_fold' is not defined"

**¿Por qué?** Intentaste ejecutar Sección 9 sin haber corrido Sección 7.

**Solución 1 (Entrenar):**
```
Ejecuta Sección 7 primero (crear results_per_fold)
Luego Sección 9 (usar results_per_fold)
```

**Solución 2 (Recargar):**
```
Ejecuta Sección 10 (crear loaded_models)
Luego Sección 9 (usar loaded_models)
```

### Problema 3: "SimpleEGNN not defined" o "ConformationPairDataset not defined"

**¿Por qué?** No ejecutaste Secciones 3-4.

**Solución:**
```
Ejecuta Secciones 1-5 en orden (sin saltar)
Todas definen clases o variables necesarias
```

### Problema 4: CUDA Out of Memory

**¿Por qué?** Modelo muy grande o batch size muy grande.

**Solución:**
```
1. Reduce EPOCHS en Sección 1 (ej: 50 → 20)
2. O usa CPU (ej: DEVICE = torch.device('cpu'))
3. O guarda checkpoints de entrenamientos previos y solo haz análisis
```

---

## 📚 Próxima Lectura

Después de completar este guide, lee:

1. **CHECKPOINT_QUICKSTART.md** - Cheat sheet rápida
2. **EGNN_CHECKPOINT_WORKFLOW.md** - Guía completa
3. **CHANGES_SUMMARY.md** - Detalles técnicos

---

## 🎓 Ejemplo Completo

### Tu Primer Ciclo Completo

```python
# Primero: Entrenar
# → Ejecuta Workflow A (Secciones 1-9)
# → Tiempo: ~2 horas
# → Output: Modelos en checkpoints/egnn_loko/

# Ahora: Reinicia Jupyter

# Después: Recargar y Analizar
# → Ejecuta Workflow B (Secciones 1-5 → 10 → 9)
# → Tiempo: ~5 minutos
# → Output: Mismo análisis sin re-entrenar

# Finalmente: Tu Análisis Personalizado
# → Usa loaded_models en Sección 11
# → Haz predicciones, visualizaciones, etc.
```

---

## ✅ Checklist Final

- [ ] Leí este guide completo
- [ ] Ejecuté Workflow A (entrenar) ó tengo checkpoints existentes
- [ ] Ejecuté Workflow B (recargar)
- [ ] Verifiqué que los checkpoints existen
- [ ] Verifiqué que los modelos reloaded funcionan
- [ ] Leí CHECKPOINT_QUICKSTART.md para referencia rápida

---

## 🤝 ¿Necesitas Ayuda?

| Si... | Lee... |
|------|--------|
| No entiendo qué cambió | RESUMEN_CAMBIOS_ES.md |
| Necesito referencia rápida | CHECKPOINT_QUICKSTART.md |
| Tengo un error específico | EGNN_CHECKPOINT_WORKFLOW.md (Troubleshooting) |
| Quiero detalles técnicos | CHANGES_SUMMARY.md |
| Necesito batch inference | egnn_batch_inference.py |

---

**Última actualización:** Junio 2026  
**Estado:** ✅ Listo para usar  
**Tiempo estimado de lectura:** 15 minutos  
**Tiempo de implementación:** 3 horas (primera vez) o 5 minutos (después)

