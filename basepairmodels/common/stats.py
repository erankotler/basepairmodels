"""

    This module contains functions to 


"""

import os 
import pyBigWig
import numpy as np

from mseqgen.quietexception import QuietException


def get_recommended_counts_loss_weight(input_bigWigs, peaks, 
                                       alpha=1.0):
    """
        This function computes the hyper parameter lambda (l) as
        suggested in the BPNet paper on pg. 28
        https://www.biorxiv.org/content/10.1101/737981v2.full.pdf
        
        if lambda `l` is set to 1/2 * n_obs, where n_obs is the 
        average number of total counts in the training set, the 
        profile loss and the  total counts loss will be roughly given 
        equal weight. We can use the `alpha` parameter to upweight 
        the profile predictions relative to the total count 
        predictions as shown below
        
        l = (alpha / 2) * n_obs
    
        Args:
            input_bigWigs (list): list of bigWig files with assay
                signal. n_obs will computed as a global average
                across all the input bigWigs
            
            peaks (list): list 3 column pandas dataframes,
                 with 'chrom', 'start' and 'end' columns,
                 corresponding to each input bigWig

            alpha (float): parameter to scale profile loss relative
                to the counts loss. A value < 1.0 will upweight the
                profile loss
    
        Returns
            float: counts loss weight (lambda)
            
    """

    # check if 'input_bigwigs' and 'peaks' have the same length
    if len(input_bigWigs) != len(peaks):
        raise QuietException("There should be same number of peaks "
                             "dataframes as input bigWigs") 
    
    # check to make sure all bigwigs are valid files
    for bigWig in input_bigWigs:
        if not os.path.exists(bigWig):
            raise QuietException("File {} does not exist".format(bigWig))

    # open each bigwig and add file pointers to a list
    bigWigs = []
    for bigWig in input_bigWigs:
        bigWigs.append(pyBigWig.open(bigWig))
    
    # total counts from all training windows across all bigwigs
    total_counts = 0
    
    # get the total counts
    total_peaks = 0
    for i in range(len(bigWigs)):
        bw = bigWigs[i]
        
        # iterate over all the corresponding peaks
        for _idx, row in peaks[i].iterrows():
            # chrom window
            chrom = row['chrom']
            start = row['start']
            end = row['end']
            total_counts += np.sum(
                np.nan_to_num(bw.values(chrom, start, end)))
        
        total_peaks += peaks[i].shape[0]
        
    # average of the total counts
    n_obs = total_counts / float(total_peaks)
    
    return (alpha / 2.0) * n_obs

            
            
        
        
        
    
