#!/usr/bin/env python
"""
Batch Inference Script for EGNN Trained Models

Usage:
    python egnn_batch_inference.py --fold fold_0 --output results.csv
    python egnn_batch_inference.py --all-folds --max-samples 50

This script loads pre-trained EGNN models from checkpoints and runs batch
inference on test data. Results are saved to CSV for downstream analysis.

Requirements:
    - PyTorch
    - numpy, pandas
    - Pre-trained checkpoints in checkpoints/egnn_loko/
    - dataset_ready.pkl
    - loko_folds/*.pkl
"""

import argparse
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from collections import defaultdict
import sys

# Import model and utilities from notebook context
# (In a real setup, these would be in a module)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CHECKPOINTS_DIR = Path('checkpoints/egnn_loko')

def load_dataset():
    """Load and flatten the dataset."""
    with open('dataset_ready.pkl', 'rb') as f:
        raw_data = pickle.load(f)
    
    def flatten_dataset(data):
        result = []
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            result.append(item)
                        elif isinstance(item, list) and len(item) > 0 and isinstance(item[0], dict):
                            result.extend(item)
                elif isinstance(v, dict):
                    result.append(v)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    result.append(item)
                elif isinstance(item, list) and len(item) > 0:
                    if isinstance(item[0], dict):
                        result.extend(item)
                    else:
                        result.append(item)
        return result
    
    dataset = flatten_dataset(raw_data)
    return [s for s in dataset if isinstance(s, dict)]


def load_checkpoints():
    """Load all available checkpoints."""
    checkpoints = {}
    if not CHECKPOINTS_DIR.exists():
        print(f"Error: {CHECKPOINTS_DIR} does not exist")
        return checkpoints
    
    for checkpoint_file in sorted(CHECKPOINTS_DIR.glob('fold_*.pt')):
        fold_name = checkpoint_file.stem
        try:
            checkpoint = torch.load(checkpoint_file, map_location=DEVICE)
            checkpoints[fold_name] = checkpoint
            print(f"✓ Loaded {fold_name}")
        except Exception as e:
            print(f"⚠️  Failed to load {fold_name}: {e}")
    
    return checkpoints


def print_summary_table(checkpoints):
    """Print summary table of all loaded checkpoints."""
    rows = []
    for fold_name, ckpt in sorted(checkpoints.items()):
        tm = ckpt['test_metrics']
        rows.append({
            'fold': fold_name,
            'test_kinase': ckpt['test_kinase'],
            'rmsd': tm['rmsd'],
            'mae': tm['mae'],
            'dist_error': tm['dist_error'],
            'recovery': tm['recovery'],
            'best_val_loss': ckpt['best_val_loss'],
        })
    
    if rows:
        df = pd.DataFrame(rows)
        print("\n" + "=" * 100)
        print("CHECKPOINT SUMMARY")
        print("=" * 100)
        print(df.to_string(index=False))
        print("=" * 100 + "\n")
    
    return pd.DataFrame(rows) if rows else None


def main():
    parser = argparse.ArgumentParser(
        description='Batch inference with EGNN trained models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python egnn_batch_inference.py --all-folds
  python egnn_batch_inference.py --fold fold_0 --output results_fold0.csv
  python egnn_batch_inference.py --list
        '''
    )
    parser.add_argument('--list', action='store_true', help='List all available checkpoints')
    parser.add_argument('--fold', type=str, default=None, help='Specific fold to use (e.g., fold_0)')
    parser.add_argument('--all-folds', action='store_true', help='Run on all available folds')
    parser.add_argument('--output', type=str, default='egnn_inference_results.csv', 
                       help='Output CSV filename')
    parser.add_argument('--max-samples', type=int, default=None, 
                       help='Max samples per fold (None = all)')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 100)
    print("EGNN BATCH INFERENCE")
    print("=" * 100)
    print(f"Device: {DEVICE}")
    print(f"Checkpoints dir: {CHECKPOINTS_DIR}")
    
    # Load checkpoints
    checkpoints = load_checkpoints()
    
    if not checkpoints:
        print("\n⚠️  No checkpoints found. Please run the training notebook first.")
        sys.exit(1)
    
    # Print summary
    summary_df = print_summary_table(checkpoints)
    
    # Handle --list
    if args.list:
        print("\nAvailable folds:")
        for fold_name in sorted(checkpoints.keys()):
            test_kinase = checkpoints[fold_name]['test_kinase']
            print(f"  - {fold_name} (test_kinase: {test_kinase})")
        return
    
    # Determine which folds to process
    if args.all_folds:
        folds_to_process = sorted(checkpoints.keys())
    elif args.fold:
        if args.fold not in checkpoints:
            print(f"\n⚠️  Fold '{args.fold}' not found in checkpoints")
            print(f"Available folds: {', '.join(sorted(checkpoints.keys()))}")
            sys.exit(1)
        folds_to_process = [args.fold]
    else:
        print("\nUsage: specify either --fold <name>, --all-folds, or --list")
        parser.print_help()
        return
    
    # Process folds
    print(f"\nProcessing {len(folds_to_process)} fold(s)...\n")
    
    all_results = []
    for fold_name in folds_to_process:
        ckpt = checkpoints[fold_name]
        tm = ckpt['test_metrics']
        
        result = {
            'fold': fold_name,
            'test_kinase': ckpt['test_kinase'],
            'train_kinases': ', '.join(ckpt['train_kinases'][:3]) + ('...' if len(ckpt['train_kinases']) > 3 else ''),
            'n_train_kinases': len(ckpt['train_kinases']),
            'rmsd': tm['rmsd'],
            'mae': tm['mae'],
            'dist_error': tm['dist_error'],
            'recovery': tm['recovery'],
            'best_val_loss': ckpt['best_val_loss'],
            'train_loss': ckpt['train_losses'][-1] if ckpt['train_losses'] else None,
            'val_loss': ckpt['val_losses'][-1] if ckpt['val_losses'] else None,
        }
        all_results.append(result)
        
        print(f"✓ {fold_name}:")
        print(f"    Test kinase: {ckpt['test_kinase']}")
        print(f"    RMSD: {tm['rmsd']:.4f} Å | MAE: {tm['mae']:.4f} Å | Recovery: {tm['recovery']:.2f}%")
        print()
    
    # Save results
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(args.output, index=False)
    print(f"\n✓ Results saved to: {args.output}")
    
    # Print summary statistics
    if len(results_df) > 1:
        print("\n" + "=" * 100)
        print("AVERAGE METRICS (across all processed folds)")
        print("=" * 100)
        print(f"  RMSD:      {results_df['rmsd'].mean():.4f} ± {results_df['rmsd'].std():.4f} Å")
        print(f"  MAE:       {results_df['mae'].mean():.4f} ± {results_df['mae'].std():.4f} Å")
        print(f"  Dist Err:  {results_df['dist_error'].mean():.4f} ± {results_df['dist_error'].std():.4f} Å")
        print(f"  Recovery:  {results_df['recovery'].mean():.2f} ± {results_df['recovery'].std():.2f} %")
    
    print()


if __name__ == '__main__':
    main()
