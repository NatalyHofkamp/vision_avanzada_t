# Quick Start: EGNN Checkpoint & Reload System

## TL;DR (Too Long; Didn't Read)

### First Time: Train Models
```
Run cells in Sección 1 → Sección 8 (in order)
✓ Models trained and saved to: checkpoints/egnn_loko/fold_*.pt
```

### After Kernel Restart: Load & Analyze (NO RE-TRAINING!)
```
1. Run Secciones 1-5 (takes ~2 min)
2. Run Sección 11 (reload checkpoints, takes ~10 sec)
3. Run Sección 10 (equivariance test, takes ~1 min)
4. Done! All results without retraining

Total time: ~5 minutes (vs. 30 min - 2 hours for full training)
```

---

## What Changed?

### ✅ CAMBIO A: Persistent Checkpoint Saving (Sección 8)

In the training loop, after each fold completes:
```python
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

**Result:** `checkpoints/egnn_loko/fold_0.pt`, `fold_1.pt`, etc.

Also saves `checkpoints/egnn_loko/all_results_summary.pkl` with summary table.

---

### ✅ CAMBIO B: New Sección 11 - Reload Checkpoints (NO RE-TRAINING)

After kernel restart, run Sección 11 to reload all saved models:

```python
# Loads all fold_*.pt files from checkpoints/egnn_loko/
# Reconstructs SimpleEGNN models with correct embedding_dim
# Stores in `loaded_models` dict ready to use

loaded_models = {
    'fold_0': {
        'model': <SimpleEGNN>,
        'test_kinase': 'ABL1',
        'test_metrics': {...},
        'train_losses': [...],
        'val_losses': [...],
        'emb_dim': 1280,
    },
    'fold_1': {...},
    ...
}
```

**Output:** Summary table showing all reloaded models and their metrics

---

### ✅ CAMBIO C: Smart Equivariance Test (Sección 10)

Adapted to use models from Sección 11 **if available**, with fallback to Sección 8:

```python
# Priority 1: Use loaded_models from Sección 11 (✓ works after restart)
# Priority 2: Use results_per_fold from Sección 8 (fallback if same session)
# Priority 3: Error message directing user what to do

if 'loaded_models' in locals():
    print("Using models from loaded_models (Sección 11)")
    # <- This works even after kernel restart!
elif 'results_per_fold' in locals():
    print("Using models from results_per_fold (Sección 8)")
else:
    print("⚠️  No models found. Run Sección 8 or 11 first.")
```

---

## File Locations

| File | Created By | Purpose |
|------|-----------|---------|
| `checkpoints/egnn_loko/fold_*.pt` | Sección 8 | Per-fold model checkpoint |
| `checkpoints/egnn_loko/all_results_summary.pkl` | Sección 8 | Results summary (optional) |
| `figures/egnn_generation/*.png` | Sección 8 | Visualization overlay plots |
| `figures/egnn_generation/loko_results_summary.csv` | Sección 8 | Results table |

---

## Key Points

1. **Checkpoints are automatic:** Sección 8 saves models without extra work
2. **Reload is fast:** Sección 11 takes ~10-30 seconds
3. **Kernel-restart safe:** No need to re-train after restarting
4. **Backward compatible:** Equivariance test works with both sources
5. **Storage efficient:** Models persist to disk, don't fill notebook memory

---

## Commands Cheat Sheet

### See what's in checkpoints/
```bash
ls -lh checkpoints/egnn_loko/
# Output:
# fold_0.pt (15 MB)
# fold_1.pt (12 MB)
# all_results_summary.pkl (50 KB)
```

### Reload and analyze (Python script):
```bash
python egnn_batch_inference.py --all-folds --output results.csv
```

### Check disk usage:
```bash
du -sh checkpoints/egnn_loko/
# Output: 150 MB (typical for ~10 folds)
```

---

## Example Workflow

### First Session
```
1. Run Secciones 1 → 8
   Time: ~1-2 hours (depends on #folds and hardware)
   Output: Trained models saved to disk
```

### Second Session (Next Day, After Kernel Restart)
```
1. Run Secciones 1 → 5     # Setup (2 min)
2. Run Sección 11          # Load models (10 sec)
3. Run Sección 10          # Test equivariance (1 min)
4. Run Sección 12          # Batch inference (1 min)

Time: ~5 minutes total (NO re-training!)
```

### Third Session (Generate New Visualizations)
```
1. Run Secciones 1 → 5     # Setup (2 min)
2. Run Sección 11          # Load models (10 sec)
3. Run custom code with loaded_models dict (1-5 min)

Time: <10 minutes
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `NameError: name 'results_per_fold' is not defined` | Run Sección 8 first OR run Sección 11 to reload |
| `No checkpoint files found in checkpoints/egnn_loko` | Run Sección 8 to generate checkpoints |
| `FileNotFoundError: dataset_ready.pkl` | Must be in same directory as notebook |
| `CUDA out of memory` | Reduce EPOCHS or use CPU (set `DEVICE` in Sección 1) |

---

## Next Steps

1. **Try it now:** Run Sección 8, then restart kernel, then run Sección 11
2. **Customize:** Modify Sección 12 for your own analysis
3. **Deploy:** Use models from `loaded_models` for downstream tasks
4. **Automate:** Use `egnn_batch_inference.py` for batch predictions

Questions? See `EGNN_CHECKPOINT_WORKFLOW.md` for detailed guide.
