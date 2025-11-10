#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 14:26:11 2018

@author: mbessani
"""

import copy as cp
from scipy import stats
import numpy as np  # biblioteca para vetores e matrizes
import matplotlib.pyplot as plt  # biblioteca para gerar figuras
import matplotlib
import pdb

matplotlib.rcParams.update({'font.size': 16})

plt.close('all')

# Resistencia

pdb.set_trace()

mu = 14
sigma = 0.4
Trunca = 13.5

Resistencia = stats.norm(loc=mu, scale=sigma)


def sample_resistencia(R=Resistencia, T=None):
    """
    Gera amostras da distribuicao da resistencia R truncadas em T
    """
    sample_semT = R.rvs(1)[0]
    sample = cp.copy(sample_semT)
    if T:
        while sample < T:  # acceptance rejection sampling
            sample = R.rvs(1)[0]
    else:
        pass
    return sample, sample_semT

# Carga


C_0 = 13
beta = 2
eta = 0.3
a = 1  # nao é a opção exponenciada- veja
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.exponweib.html#scipy.stats.exponweib

Carga = stats.exponweib(a=a, scale=eta, c=beta, loc=0)


def sample_carga(C=Carga, C_0=C_0):
    sample = C.rvs(1)[0] + C_0
    return sample


N = 10000
resistencias = np.zeros(N)
resistencias_semT = np.zeros(N)
cargas = np.zeros(N)

for n in range(N):
    resistencias[n], resistencias_semT[n] = sample_resistencia(
        Resistencia, T=Trunca)
    cargas[n] = sample_carga()

# plt.figure(dpi=100)
# plt.hist(cargas, density=False, bins=100,
#          histtype='stepfilled', lw=2, alpha=0.8, label='Cargas')
# plt.hist(resistencias, density=False, bins=100, histtype='step',
#          lw=2, alpha=0.8, label='Resistência')
# plt.title('Com truncamento')
# plt.legend()


plt.figure(dpi=100)
plt.hist(cargas, density=False, bins=100,
         histtype='stepfilled', lw=2, alpha=0.8, label='Cargas')
plt.hist(resistencias_semT, density=False, bins=100, histtype='step',
         lw=2, alpha=0.8, label='Resistência')
plt.title('Sem truncamento')
plt.legend()
plt.show()

# result = resistencias - cargas
# p_falha = (result <= 0).sum()/N  # Estimativa de P(S<=L)
# print('Probabilidade de Falha: %0.4f' % (p_falha))
# R = 1-p_falha  # Estimativa de R = P(S>L)
# RT = 1-p_falha
# print('Confiabilidade: %0.4f' % (R))


result = resistencias_semT - cargas
p_falha = (result <= 0).sum()/N  # Estimativa de P(S<=L)
print('Probabilidade de Falha sem Truncamento: %0.4f' % (p_falha))
R = 1-p_falha  # Estimativa de R = P(S>L)
print('Confiabilidade sem Truncamento: %0.4f' % (R))
