r"""torecsys.data.negsampling is a module of negative sampling algorithms.
"""
import torch
from torecsys.utils.operations import replicate_tensor
from typing import Dict

class _NegativeSampler(object):
    r"""Base class of negative sampler. Negative sampler will be called by RankingTrainer and 
    generate negative samples for each iteration to calculate pairwise ranking loss.
    """
    def __init__(self, 
                 kwargs_dict: Dict[str, Dict[str, int]]):
        r"""Initialize _NegativeSampler.
        
        Args:
            kwargs_dict (Dict[str, Dict[str, int]]): A dictionary, where key is field's name 
                and value, including low and high, is a dictionary, where key is name of 
                argument and value is value of argument.
        """
        self.kwargs_dict = kwargs_dict
        self.dict_size = self._getlen(kwargs_dict)
    
    def _getlen(self) -> int:
        r"""Get length of field.
        
        Raises:
            NotImplementedError: when the function `_getlen` is not implemented.
        
        Returns:
            int: Length of field.
        """
        raise NotImplementedError("_getlen is not implemented in Base Class.")

    def __len__(self) -> Dict[str, int]:
        r"""Return size of dictionary.
        
        Returns:
            Dict[str, int]: A dictionary, where key is field's name and value is the total number of words in that field
        """
        return self.dict_size

    def size(self) -> Dict[str, int]:
        r"""Return size of dictionary.
        
        Returns:
            Dict[str, int]: A dictionary, where key is field's name and value is the total number of words in that field
        """
        return __len__()

    def __call__(self, *args, **kwargs) -> Dict[str, torch.Tensor]:
        """Return drawn samples.
        
        Args:
            pos_samples (Dict[str, T]): A dictionary of positive samples, where key is field's name and value is 
                the tensor of that field with shape = (N, 1) and dtype = torch.long.
            size (int): An integer of number of negative samples to be generated.
        
        Returns:
            Dict[str, T]: A dictionary of negative samples, where key is field's name and value is the tensor of 
                that field with shape = (N * Nneg, 1) and dtype = torch.long.
        """
        return self.generate(*args, **kwargs)
    
    def _generate(self) -> torch.Tensor:
        """A function to generate negative samples.
        
        Raises:
            NotImplementedError: when the function `_generate` is not implemented.
        
        Returns:
            T, shape = (N * Nneg, 1), dtype = torch.long: Tensor of negative samples generated by the given function.
        """
        raise NotImplementedError("_generate is not implemented in Base Class.")
    
    def generate(self, 
                 pos_samples: Dict[str, torch.Tensor], 
                 size: int) -> Dict[str, torch.Tensor]:
        """Return drawn samples.
        
        Args:
            pos_samples (Dict[str, T]): A dictionary of positive samples, where key is field's name and value is 
                the tensor of that field with shape = (N, ...) and dtype = torch.long.
            size (int): An integer of number of negative samples to be generated.
        
        Returns:
            Dict[str, T]: A dictionary of negative samples, where key is field's name and value is the tensor of 
                that field with shape = (N * Nneg, ...) and dtype = torch.long.
        """
        # Get field in sampler which is to replace by sampler,
        keys = list(self.kwargs_dict.keys())
        
        neg_samples = {}
        
        for k, v in pos_samples.items():
            if k in keys:
                # TODO: handle generate sample with dim > 2

                # Generate negative samples with sampler.
                # Get batch size of field and calculate number of samples to be generated.
                batch_size = v.size(0)
                num_neg = size * batch_size
                
                # Get arguments of the field to be called in _generate.
                kwargs = self.kwargs_dict[k]
                kwargs["size"] = num_neg
                
                # Generate the negative samples.
                neg_samples[k] = self._generate(**kwargs)
                
            else:
                # replicate values to be negative samples
                # inputs: v, shape = (B, ...)
                # output: neg_samples[k], shape = (B * size, ...)
                neg_samples[k] = replicate_tensor(v, size, dim=1)
        
        return neg_samples

from .multinomial_sampler import MultinomialSampler
from .uniform_sampler import UniformSamplerWithoutReplacement
from .uniform_sampler import UniformSamplerWithReplacement
