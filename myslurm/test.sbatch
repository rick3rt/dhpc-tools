#!/bin/sh

#SBATCH --partition=compute
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=2
#SBATCH --mail-type=BEGIN,END
#SBATCH --account=research-as-imphys

#SBATCH --output=slog/%x-%j.out

# ==============================================================================
# Your job commands go below here
# ==============================================================================

# Uncomment these lines when your job requires this software
#module use /opt/insy/modulefiles
module load 2022r2
module load matlab
module load cuda

# Complex or heavy commands should be started with 'srun' (see 'man srun' for more information)
echo matlab -nodesktop -r "exec_run('$DATA_LOAD_PATH', $NUM)"
srun hostname | sort
