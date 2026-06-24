# EGNN Generative Model: Checkpoint & Workflow Guide

## Overview

The `04_egnn_generate_active.ipynb` notebook implements a robust EGNN (Equivariant Graph Neural Network) that learns the INACTIVE→ACTIVE structural transformation of kinase conformations using a LOKO (Leave-One-Kinase-Out) cross-validation scheme.

**Key Feature: Checkpoint Persistence**

All trained models are automatically saved to disk after each fold, allowing you to:
- Reload trained models without retraining (kernel restart safe)
- Run analysis/visualization independently
- Batch-process predictions on new data

---

## Workflow Modes

### Mode 1: Full Training Pipeline (First Run)

**Recommended for initial exploration and model development.**

```
Sección 1 → Cargar e inspeccionar dataset
    ↓
Sección 2 → Construir pares INACTIVE→ACTIVE por kinasa
    ↓
Sección 3 → Dataset class + collate function
    ↓
Sección 4 → Modelo EGNN
    ↓
Sección 5 → Funciones loss, métricas
    ↓
Sección 6 → Cargar folds LOKO
    ↓
Sección 7 → *** TRAINING LOOP (creates checkpoints) ***
    ↓ (checkpoints/ saved to disk after each fold)
    ↓
Sección 8 → Scientific Summary
    ↓
Sección 9 → Equivariance Test (uses in-memory models)
    ↓
Sección 10 → Batch Inference Utilities
```

**Expected outputs:**
- `/checkpoints/egnn_loko/fold_*.pt` - individual fold checkpoints
- `/checkpoints/egnn_loko/all_results_summary.pkl` - summary pickle
- `/figures/egnn_generation/` - visualization files

---

### Mode 2: Analysis After Kernel Restart (Recommended)

**Use this after restarting your Jupyter kernel to avoid re-training.**

```
Sección 1 → Cargar dataset (required for data structures)
    ↓
Sección 2 → Construir pares (required for dataset class)
    ↓
Sección 3 → Dataset class + collate (required)
    ↓
Sección 4 → Modelo EGNN (required for reconstruction)
    ↓
Sección 5 → Funciones loss/métricas (required)
    ↓
Sección 6 → Cargar folds LOKO (optional, not used in this mode)
    ↓
[SKIP Sección 7: No re-training]
    ↓
[SKIP Sección 8: No training logging]
    ↓
Sección 11 → *** RELOAD MODELS FROM CHECKPOINTS ***
    ↓ (loads previously trained models into `loaded_models` dict)
    ↓
Sección 10 → Equivariance Test (uses reloaded models)
    ↓
Sección 12 → Batch Inference & Visualization
```

**Requirements:**
- Checkpoints must exist in `checkpoints/egnn_loko/`
- Must run Secciones 1-5 first (data structures & model class)

**Benefits:**
- No re-training (fast!)
- Can verify model convergence from saved training curves
- Can run equivariance tests on reloaded models

---

### Mode 3: Custom Analysis Only

**Use if you only want to analyze existing results without the full pipeline.**

```
Setup Phase:
  - Run Secciones 1-5 (model infrastructure)
  
Analysis Phase:
  - Run Sección 11 (reload checkpoints)
  - Run Sección 10 (equivariance test with reloaded models)
  - Run Sección 12 (batch inference on new data)
```

---

## Checkpoint Structure

### Per-Fold Checkpoints

**File:** `checkpoints/egnn_loko/fold_<name>.pt`

**Contents:**
```python
checkpoint = {
    'model_state_dict': dict,        # PyTorch model weights
    'emb_dim': int,                  # embedding dimension
    'fold_name': str,                # e.g., 'fold_0'
    'test_kinase': str,              # kinase held-out for testing
    'train_kinases': list,           # kinases used for training
    'train_losses': list,            # per-epoch training loss
    'val_losses': list,              # per-epoch validation loss
    'test_metrics': dict,            # {rmsd, mae, dist_error, recovery}
    'best_val_loss': float,          # best validation loss achieved
}
```

### Summary Pickle

**File:** `checkpoints/egnn_loko/all_results_summary.pkl`

Contains:
- `results_df`: DataFrame with per-fold results
- `checkpoints_dir`: path to checkpoint directory
- `folds_trained`: list of trained fold names

---

## Section Details

### Sección 8: Training Loop

**Saves checkpoints automatically after each fold.**

```python
# Inside the fold loop:
checkpoint_path = checkpoints_dir / f"{fold_name}.pt"
torch.save({
    'model_state_dict': model.state_dict(),
    'emb_dim': emb_dim,
    'fold_name': fold_name,
    'test_kinase': test_kinase,
    'train_kinases': train_kinases,
    'train_losses': train_losses,
    'val_losses': val_losses,
    'test_metrics': test_metrics,
    'best_val_loss': best_val_loss,
}, checkpoint_path)
```

**Output messages:**
```
✓ Checkpoint saved: checkpoints/egnn_loko/fold_0.pt
✓ Checkpoint saved: checkpoints/egnn_loko/fold_1.pt
...
```

### Sección 11: Reload Checkpoints

**Reconstructs models from saved checkpoints.**

```python
# For each checkpoint file:
checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
model = SimpleEGNN(...).to(DEVICE)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

loaded_models[fold_name] = {
    'model': model,
    'test_kinase': checkpoint['test_kinase'],
    'test_metrics': checkpoint['test_metrics'],
    ...
}
```

**Output:** Summary table of reloaded models with metrics

```
fold    test_kinase  rmsd     mae      dist_err  recovery  best_val_loss
fold_0  ABL1         0.8234   0.5123   1.2345    78.50     0.0456
fold_1  FGFR1        0.7891   0.4956   1.1203    81.23     0.0392
...
```

### Sección 10: Equivariance Test

**Tests rotational equivariance on reloaded (or in-memory) models.**

Uses priority:
1. `loaded_models` from Sección 11 (primary)
2. `results_per_fold` from Sección 8 (fallback if same session)
3. Skip if neither available

**Output:**
```
ROTATIONAL EQUIVARIANCE TEST
================================================================================

✓ Using models from loaded_models (Sección 11)

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
✓ Source: LOADED FROM CHECKPOINTS (Sección 11)
```

### Sección 12: Batch Inference

**Utilities for running predictions on multiple samples.**

```python
batch_inference_on_fold(
    model,
    test_pairs,
    fold_name='fold_0',
    kinase_name='ABL1',
    max_samples=10,
    device=DEVICE
)
```

Returns:
```python
{
    'fold_name': 'fold_0',
    'kinase_name': 'ABL1',
    'n_samples': 10,
    'predictions': [
        {'pair_idx': 0, 'predicted_coords': ..., 'true_coords': ..., 
         'rmsd': 0.82, 'mae': 0.51},
        ...
    ],
    'mean_rmsd': 0.82,
    'mean_mae': 0.51,
}
```

---

## Common Use Cases

### Use Case 1: Train Models and Save

```python
# Run cells in order: Secciones 1 → 8
# Checkpoints are saved automatically after each fold
# Training time depends on dataset size and hardware
```

### Use Case 2: Reload and Analyze After Restart

```python
# After kernel restart:
# 1. Run Secciones 1-5 (setup, takes ~1-2 minutes)
# 2. Run Sección 11 (reload, takes ~10-30 seconds depending on # checkpoints)
# 3. Run Sección 10 (equivariance test, takes ~1-2 minutes)
# 4. Run Sección 12 (batch inference, fast)

# Total time: ~5-10 minutes (no retraining!)
```

### Use Case 3: Extract Model Weights

```python
model_info = loaded_models['fold_0']
model = model_info['model']

# Save to custom format or export for deployment
torch.save(model.state_dict(), 'my_egnn_weights.pt')

# Or access architecture info
emb_dim = model_info['emb_dim']  # 1280
```

### Use Case 4: Evaluate on New Data

```python
# Create new pairs (not in LOKO splits)
new_pairs = [...]

# Run inference on new data
result = batch_inference_on_fold(
    loaded_models['fold_0']['model'],
    new_pairs,
    fold_name='fold_0',
    kinase_name='ABL1',
    max_samples=100
)

print(f"Mean RMSD on new data: {result['mean_rmsd']:.4f} Å")
```

---

## Troubleshooting

### Problem: "NameError: name 'results_per_fold' is not defined"

**Cause:** Running Sección 10 without having run Sección 8 first.

**Solution:** Either:
1. Run Sección 8 to train models, OR
2. Run Sección 11 to load existing checkpoints

### Problem: "No checkpoint files found in checkpoints/egnn_loko"

**Cause:** Checkpoints haven't been created yet.

**Solution:** Run Sección 8 (training loop) to generate checkpoints.

### Problem: Models have different embedding dimensions

**Cause:** Different kinases have different sequence lengths → different embedding dims.

**Solution:** This is expected. Each model has its own `emb_dim` stored in the checkpoint and is automatically reconstructed when loading.

### Problem: Out of Memory (OOM) during training

**Cause:** Batch size or model size too large.

**Solution:**
- Reduce `EPOCHS` in Sección 1
- Use checkpoints from previous runs
- Run analysis (Secciones 10-12) which use smaller batches

---

## Performance Notes

| Operation | Time (approx) | Hardware Dependent |
|-----------|---------------|-------------------|
| Secciones 1-5 setup | 1-2 min | CPU-bound, minimal GPU use |
| Sección 8 training (all folds) | 30 min - 2 hours | GPU-bound, very dependent |
| Sección 11 reload | 10-30 sec | Disk I/O + CPU |
| Sección 10 equivariance test | 1-2 min | GPU-bound |
| Sección 12 batch inference | Fast (~1-10 sec per fold) | GPU-bound |

**GPU availability:** Check with `torch.cuda.is_available()` at start of notebook.

---

## File Locations

```
/home/user/tpf2/vision_avanzada_tpf/
├── 04_egnn_generate_active.ipynb          ← Main notebook
├── dataset_ready.pkl                      ← Input dataset
├── data/
│   └── loko_folds/
│       ├── fold_0.pkl
│       ├── fold_1.pkl
│       └── ...
├── checkpoints/                           ← Created by Sección 8
│   └── egnn_loko/
│       ├── fold_0.pt                      ← Per-fold model
│       ├── fold_1.pt
│       ├── ...
│       └── all_results_summary.pkl        ← Summary
└── figures/                               ← Created by Sección 8
    └── egnn_generation/
        ├── fold_0_sample0_overlay.png
        ├── fold_0_sample1_overlay.png
        └── loko_results_summary.csv
```

---

## Next Steps

1. **First time:** Run Secciones 1-9 for full exploration
2. **Kernel restart:** Run Secciones 1-5, then 11-12
3. **Custom analysis:** Extend Sección 12 with your own visualization/metrics
4. **Deployment:** Extract model weights from `loaded_models` dictionary

Happy modeling! 🧬🔬

