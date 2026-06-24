# Visual Guide: Checkpoint System Architecture

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOTEBOOK EXECUTION FLOW                      │
└─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════
SETUP PHASE (Secciones 1-5)
═══════════════════════════════════════════════════════════════════

    ┌─────────────────┐
    │  Sección 1      │ Imports, device, hyperparams
    │  (Imports)      │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Sección 2      │ Load & flatten dataset
    │  (Dataset)      │ dataset = [1234 dicts]
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Sección 3      │ Dataset class + collate
    │  (Classes)      │ ConformationPairDataset
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Sección 4      │ Model architecture
    │  (Model)        │ SimpleEGNN (embedding_dim=1280, ...)
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Sección 5      │ Loss, metrics, train/val functions
    │  (Functions)    │ masked_mse_loss, compute_metrics_batch
    └────────┬────────┘
             │
         [READY]

═══════════════════════════════════════════════════════════════════
TRAINING PATH (Sección 7)
═══════════════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────────────────┐
    │  Sección 6: Load LOKO folds                             │
    │  loko_datasets = {fold_0: {...}, fold_1: {...}, ...}   │
    └─────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────▼──────────────────────────────────────────┐
    │  Sección 7: TRAINING LOOP (🎯 SAVES CHECKPOINTS HERE) │
    │                                                         │
    │  for each fold:                                         │
    │    - Train model with DataLoader                        │
    │    - Compute val_loss, best_val_loss                    │
    │    - Evaluate on test set                               │
    │    - results_per_fold[fold_name] = {...}               │
    │                                                         │
    │    💾 CHECKPOINT SAVING:                               │
    │    torch.save({                                         │
    │      'model_state_dict': model.state_dict(),           │
    │      'emb_dim': 1280,                                  │
    │      'test_kinase': 'ABL1',                            │
    │      'train_losses': [...],                             │
    │      'test_metrics': {...},                             │
    │      ...                                                │
    │    }, checkpoints/egnn_loko/fold_0.pt)                 │
    │                                                         │
    │    💾 SUMMARY PICKLE:                                  │
    │    pickle.dump(all_results_summary,                     │
    │      checkpoints/egnn_loko/all_results_summary.pkl)    │
    │                                                         │
    └─────────────┬──────────────────────────────────────────┘
                  │
         ┌────────▼────────────────────────────┐
         │ results_per_fold (in-memory)        │
         │ {fold_0: {...}, fold_1: {...}, ...} │
         │ (exists until kernel restart)       │
         └────────┬─────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────┐
    │ Secciones 8-9: Analysis using results_per_fold │
    │ - Scientific Summary                            │
    │ - Equivariance Test (uses results_per_fold)    │
    └─────────────┬───────────────────────────────────┘
                  │
              [✓ OK]


═══════════════════════════════════════════════════════════════════
RELOAD PATH (After Kernel Restart)
═══════════════════════════════════════════════════════════════════

    ┌──────────────────────────────────────────────┐
    │ Kernel Restart ← results_per_fold LOST ✗     │
    │                ← But checkpoints saved on disk! ✓
    └──────────────────────┬───────────────────────┘
                           │
    ┌──────────────────────▼───────────────────────┐
    │ Secciones 1-5: Re-run setup                 │
    │ (Recreates dataset, model classes, etc.)    │
    │ (~2 minutes)                                 │
    └──────────────────────┬───────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────┐
    │ Sección 10: RELOAD CHECKPOINTS (NEW!)             │
    │                                                    │
    │ for each fold_*.pt in checkpoints/egnn_loko/:    │
    │   - torch.load(fold_N.pt)                          │
    │   - Create SimpleEGNN(embedding_dim=...)           │
    │   - model.load_state_dict(checkpoint[...])        │
    │   - model.eval()                                   │
    │                                                    │
    │ loaded_models = {                                  │
    │   'fold_0': {'model': <SimpleEGNN>, ...},         │
    │   'fold_1': {'model': <SimpleEGNN>, ...},         │
    │   ...                                              │
    │ }                                                  │
    │                                                    │
    │ Print summary table with test_metrics             │
    │ (~10 seconds)                                      │
    └──────────────────────┬───────────────────────────────┘
                           │
         ┌─────────────────▼──────────────────────┐
         │ loaded_models (from disk)              │
         │ {fold_0: {...}, fold_1: {...}, ...}   │
         │ (ready for immediate use)              │
         └─────────────────┬──────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────┐
    │ Sección 9: Analysis using loaded_models        │
    │ - Equivariance Test (uses loaded_models)       │
    │ - Batch Inference                              │
    │ - Custom analysis                              │
    └──────────────────────┬───────────────────────────┘
                           │
                       [✓ OK]


═══════════════════════════════════════════════════════════════════
CHECKPOINT DATA STRUCTURE
═══════════════════════════════════════════════════════════════════

checkpoint = {
    'model_state_dict': OrderedDict([       ← Neural network weights
        ('layer0.weight', tensor([...])),
        ('layer0.bias', tensor([...])),
        ('layer1.weight', tensor([...])),
        ...
    ]),
    
    'emb_dim': 1280,                        ← Embedding dimension
    'fold_name': 'fold_0',                  ← Fold identifier
    'test_kinase': 'ABL1',                  ← Test kinase (LOKO)
    'train_kinases': ['FGFR1', 'SRC', ...], ← Train kinases
    
    'train_losses': [0.234, 0.189, 0.145, ...],  ← Per-epoch train
    'val_losses': [0.245, 0.201, 0.167, ...],    ← Per-epoch val
    'best_val_loss': 0.0456,                     ← Best validation
    
    'test_metrics': {                       ← Final test scores
        'rmsd': 0.8234,
        'mae': 0.5123,
        'dist_error': 1.2345,
        'recovery': 78.50,
    }
}

File: checkpoints/egnn_loko/fold_0.pt (~15 MB)
Persists until: manually deleted
Accessible after: kernel restart ✓


═══════════════════════════════════════════════════════════════════
MODEL SOURCING LOGIC IN SECTION 9 (Equivariance Test)
═══════════════════════════════════════════════════════════════════

    Start Section 9
           │
    ┌──────▼────────────────────────────────┐
    │ Check: 'loaded_models' in locals()?   │
    │        and len(loaded_models) > 0?    │
    └──┬─────────────────────────────────┬──┘
       │ YES                             │ NO
       │                                  │
    ┌──▼──────────────────────────┐   ┌──▼──────────────────────────┐
    │ Use loaded_models           │   │ Check: 'results_per_fold'?  │
    │ (from Sección 10 reload)   │   │        in locals()?         │
    │                             │   │        len > 0?             │
    │ models_source =             │   └──┬──────────────────────┬───┘
    │ "LOADED FROM CHECKPOINTS"  │      │ YES              │ NO
    │                             │      │                   │
    │ Print: ✓ using loaded_...   │   ┌──▼─────────────────┐ │
    └──────────────────────────────┘   │ Use results_per_   │ │
                                       │ fold (in-memory)   │ │
                                       │                    │ │
                                       │ models_source =    │ │
                                       │ "FROM TRAINING.." │ │
                                       │                    │ │
                                       │ Print: ✓ using     │ │
                                       │ results_per_fold   │ │
                                       └──────────────────────┘ │
                                                                 │
                                                    ┌────────────▼──┐
                                                    │ Neither found │
                                                    │               │
                                                    │ Print: ⚠️     │
                                                    │ No models.    │
                                                    │ Run Sección   │
                                                    │ 7 or 10 first │
                                                    │               │
                                                    │ Skip tests    │
                                                    └────────────────┘

    All paths → Run equivariance tests on available models
               └─ Print source (checkpoint vs. in-memory)
```

---

## 📊 Time Comparison Diagram

```
WORKFLOW A: First-Time Training
═════════════════════════════════════════════════════

Sección 1-5 (Setup):     ███░░░░░░░░░░░░░░░░░░░░ 15 min
Sección 7 (TRAINING):   ██████████████████████████ 1-2 hours ⏳
Sección 8-9 (Analysis): ░░░░░░░░░░░░░░░░░░░░░░░░ 3 min
                        ─────────────────────────────────
                        TOTAL: 1.5-2.5 hours


WORKFLOW B: After Kernel Restart (NEW!)
═════════════════════════════════════════════════════

Sección 1-5 (Setup):     ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 2 min
Sección 10 (RELOAD):    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 10 sec
Sección 9 (Analysis):   ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 2 min
                        ──────────────────────────────────────────────────────────
                        TOTAL: ~5 minutes ⚡⚡⚡ (15-30x FASTER!)


SPEEDUP FACTOR:
═════════════════════════════════════════════════════

Old way (re-train):     ████████████████████████████████ 1-2 hours
New way (reload):       ██ ~5 minutes

Speedup: 15-30x faster! ⚡⚡⚡
```

---

## 🔄 State Transitions

```
MEMORY STATE (in Jupyter kernel):

Session 1:
┌──────────────────────────────────────┐
│ Run Secciones 1-7                    │
├──────────────────────────────────────┤
│ results_per_fold = {                 │ ← In memory
│   'fold_0': {...},                   │
│   'fold_1': {...},                   │
│   ...                                │
│ }                                    │
└──────────────────────────────────────┘
        │
        │ Can use for Sección 9 (equivariance test)
        ▼


Kernel Restart:
┌──────────────────────────────────────┐
│ results_per_fold = DELETED ✗         │ ← Lost!
│ (kernel memory cleared)              │
└──────────────────────────────────────┘
        │
        │ BUT: checkpoints/ on disk persists ✓
        ▼


Session 2:
┌──────────────────────────────────────┐
│ Run Sección 10                       │
├──────────────────────────────────────┤
│ loaded_models = {                    │ ← Recreated from disk
│   'fold_0': {'model': ..., ...},     │
│   'fold_1': {'model': ..., ...},     │
│   ...                                │
│ }                                    │
└──────────────────────────────────────┘
        │
        │ Can use for Sección 9 (equivariance test)
        ▼
```

---

## 💾 File System

```
Working Directory:
/home/user/tpf2/vision_avanzada_tpf/

├── 📔 04_egnn_generate_active.ipynb
│
├── 📂 checkpoints/                     ← CREATED BY SECCIÓN 7
│   └── egnn_loko/
│       ├── fold_0.pt                   (~15 MB) Contains:
│       │                               - Model weights
│       │                               - Metadata
│       │                               - Metrics
│       │
│       ├── fold_1.pt                   (~12 MB)
│       ├── fold_2.pt                   (~14 MB)
│       ├── ...
│       │
│       └── all_results_summary.pkl     (~50 KB)
│           Results DataFrame
│           + metadata
│
├── 📂 data/
│   └── loko_folds/                     ← Input (must pre-exist)
│       ├── fold_0.pkl
│       ├── fold_1.pkl
│       └── ...
│
├── 📂 figures/
│   └── egnn_generation/                ← CREATED BY SECCIÓN 7
│       ├── fold_0_sample0_overlay.png
│       ├── fold_0_sample1_overlay.png
│       ├── fold_1_sample0_overlay.png
│       └── loko_results_summary.csv
│
├── 📄 dataset_ready.pkl                ← Input (must pre-exist)
│
└── 📚 DOCUMENTATION
    ├── RESUMEN_CAMBIOS_ES.md           (Exec summary in Spanish)
    ├── CHECKPOINT_QUICKSTART.md        (Quick reference)
    ├── EGNN_CHECKPOINT_WORKFLOW.md     (Full guide)
    ├── CHANGES_SUMMARY.md              (Technical details)
    ├── GETTING_STARTED.md              (Step-by-step guide)
    ├── README_CHECKPOINT_DOCS.md       (Documentation index)
    └── egnn_batch_inference.py         (CLI tool)
```

---

## 🎯 Decision Tree: Which Workflow?

```
                    ┌─ Start
                    │
        ┌───────────▼──────────────┐
        │ Do you have             │
        │ checkpoints/ already?    │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐         ┌─────────────────────────┐
        │ YES                    │         │ NO                      │
        │ (From previous run)    │         │ (First time)            │
        └───────────┬──────────────┘         └────────────┬──────────┘
                    │                                     │
            ┌───────▼────────────┐               ┌────────▼──────────┐
            │ Workflow B:        │               │ Workflow A:      │
            │ 1. Run Sec 1-5     │               │ 1. Run Sec 1-7   │
            │ 2. Run Sec 10      │               │ 2. This creates  │
            │ 3. Run Sec 9       │               │    checkpoints   │
            │ 4. Run Sec 11      │               │ 3. Then run      │
            │                    │               │    Sec 8-9       │
            │ Time: ~5 min ⚡    │               │ 4. Save those    │
            │ (NO re-train)      │               │    checkpoints   │
            └────────┬───────────┘               │                  │
                     │                           │ Time: 1-2h ⏳    │
                     │                           │ (First time)     │
                     │                           └────────┬──────────┘
                     │                                    │
                ┌────▴────────────────────┬──────────────┘
                │                         │
        ┌───────▼─────────┐       ┌───────▼────────┐
        │ Quick analysis  │       │ Next session:  │
        │ of results      │       │ Go to Workflow │
        │ (no re-train)   │       │ B (above)      │
        └─────────────────┘       └────────────────┘
```

---

## 📈 Performance Metrics

```
GPU Utilization During Training (Sección 7):
═══════════════════════════════════════════════════

Time →
GPU% │
100% │    ╔════════════════════════════════════════╗
     │    ║                                        ║
 80% │    ║   Training loop running                ║
     │    ║   Model forward/backward passes        ║
 60% │    ║   Optimizer updates                    ║
     │    ║╝                                        ║
 40% │╔════╣                      ╔════════════════╝
     │║    ║                      ║ Validation
 20% │║    ║                      ║ (lower GPU use)
     │║    ║                      ║
  0% ╚════════════════════════════╩════════════════════
     └─────────────────────────────────────────────────


GPU Memory Usage During Inference (Sección 10):
═════════════════════════════════════════════════

Model Loaded: ~500 MB per fold
Batch inference: ~100-200 MB additional


Disk Usage:
═══════════

Per fold checkpoint: ~10-20 MB
5 folds: ~60-100 MB total
all_results_summary.pkl: ~50 KB

Total on disk: ~100-150 MB (very reasonable!)
```

---

This visual guide helps understand:
✅ How the system flows from training to reload  
✅ The exact moment checkpoints are saved  
✅ What happens at kernel restart  
✅ How model sourcing prioritizes loaded_models  
✅ File locations and sizes  
✅ Time savings (15-30x faster!)  

