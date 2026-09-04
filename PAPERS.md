# Bibliography — Cited Corpus

This is the reference list for the document corpus used in **Cited**. PDFs themselves are not
committed to this repo (see `.gitignore`) — download each paper from the link given, or from
your own copy, and place it in `data/raw_papers/` before running ingestion.

Scope: unsupervised and self-supervised approaches to semantic segmentation and representation
learning, with an applied emphasis on high-resolution remote sensing imagery.

---

## Anchor paper

- T. Sharma, I. Baranwal, N. Badal, B. Bansal, A. Sharma — "Unsupervised Segmentation of
  High-Resolution Multispectral Satellite Images," IEEE InGARSS 2025

---

## A. Core segmentation architectures & benchmarks

1. J. Long, E. Shelhamer, T. Darrell — "Fully Convolutional Networks for Semantic Segmentation,"
   CVPR 2015
2. O. Ronneberger, P. Fischer, T. Brox — "U-Net: Convolutional Networks for Biomedical Image
   Segmentation," MICCAI 2015
3. L.-C. Chen, G. Papandreou, I. Kokkinos, K. Murphy, A. L. Yuille — "DeepLab: Semantic Image
   Segmentation with Deep Convolutional Nets, Atrous Convolution, and Fully Connected CRFs,"
   [arXiv:1606.00915](https://arxiv.org/abs/1606.00915), 2016
4. E. Maggiori, Y. Tarabalka, G. Charpiat, P. Alliez — "Can Semantic Labeling Methods Generalize
   to Any City? The Inria Aerial Image Labeling Benchmark," IGARSS 2017
5. J. Shi, J. Malik — "Normalized Cuts and Image Segmentation," IEEE TPAMI, vol. 22, no. 8, 2000
6. A. Y. Ng, M. I. Jordan, Y. Weiss — "On Spectral Clustering: Analysis and an Algorithm,"
   NeurIPS 2001
7. T. Chen, S. Kornblith, M. Norouzi, G. Hinton — "A Simple Framework for Contrastive Learning
   of Visual Representations (SimCLR)," ICML 2020
8. K. He, H. Fan, Y. Wu, S. Xie, R. Girshick — "Momentum Contrast for Unsupervised Visual
   Representation Learning (MoCo)," CVPR 2020
9. M. Caron, I. Misra, J. Mairal, P. Goyal, P. Bojanowski, A. Joulin — "Unsupervised Learning of
   Visual Features by Contrasting Cluster Assignments (SwAV)," NeurIPS 2020
10. A. van den Oord, O. Vinyals, K. Kavukcuoglu — "Neural Discrete Representation Learning
    (VQ-VAE)," [arXiv:1711.00937](https://arxiv.org/abs/1711.00937), 2017
11. C. M. Bishop — *Pattern Recognition and Machine Learning*, Springer, 2006
12. J. J. Hwang, T. Liu, Y.-H. Yang, M.-H. Yang — "SegSort: Segmentation by Discriminative
    Sorting of Segments," ICCV 2019
13. H. Macedo, Y. Bazi, H. Alhichri, F. Melgani — "Unsupervised Single-Scene Semantic
    Segmentation for Earth Observation," ISPRS J. Photogramm. Remote Sens., vol. 186, 2022
14. H. Zhao, O. Gallo, I. Frosio, J. Kautz — "Loss Functions for Image Restoration with Neural
    Networks (MS-SSIM)," [arXiv:1511.08861](https://arxiv.org/abs/1511.08861), 2018
15. A. Kirillov, E. Mintun, N. Ravi, et al. — "Segment Anything (SAM),"
    [arXiv:2304.02643](https://arxiv.org/abs/2304.02643), 2023
16. M. P. Barbato, P. Napoletano, F. Piccoli, R. Schettini — "Unsupervised Segmentation of
    Hyperspectral Remote Sensing Images with Superpixels,"
    [arXiv:2204.12296](https://arxiv.org/abs/2204.12296), 2024
17. A. B. Metzler, R. Nathvani, V. Sharmanska, et al. — "Unsupervised Deep Clustering of
    High-Resolution Satellite Imagery Reveals Phenotypes of Urban Development in Sub-Saharan
    Africa," Science of the Total Environment, vol. 988, 2025
18. R. Achanta, A. Shaji, K. Smith, A. Lucchi, P. Fua, S. Süsstrunk — "SLIC Superpixels Compared
    to State-of-the-Art Superpixel Methods," IEEE TPAMI, vol. 34, no. 11, 2012

## B. Unsupervised / self-supervised semantic segmentation

19. X. Ji, J. F. Henriques, A. Vedaldi — "Invariant Information Clustering for Unsupervised
    Image Classification and Segmentation (IIC)," ICCV 2019
20. J. H. Cho, U. Mall, K. Bala, B. Hariharan — "PiCIE: Unsupervised Semantic Segmentation Using
    Invariance and Equivariance in Clustering," [arXiv:2103.17070](https://arxiv.org/abs/2103.17070), CVPR 2021
21. M. Hamilton, Z. Zhang, B. Hariharan, N. Snavely, W. T. Freeman — "STEGO: Unsupervised
    Semantic Segmentation by Distilling Feature Correspondences,"
    [arXiv:2203.08414](https://arxiv.org/abs/2203.08414), ICLR 2022
22. X. Xia, B. Kulis — "W-Net: A Deep Model for Fully Unsupervised Image Segmentation,"
    [arXiv:1711.08506](https://arxiv.org/abs/1711.08506), 2017
23. W. Kim, A. Kanezaki, M. Tanaka — "Unsupervised Learning of Image Segmentation Based on
    Differentiable Feature Clustering," IEEE Trans. Image Processing, 2020
24. W. Van Gansbeke, S. Vandenhende, S. Georgoulis, M. Proesmans, L. Van Gool — "SCAN: Learning
    to Classify Images Without Labels," ECCV 2020
25. W. Van Gansbeke, S. Vandenhende, S. Georgoulis, L. Van Gool — "Unsupervised Semantic
    Segmentation by Contrasting Object Mask Proposals,"
    [arXiv:2102.06191](https://arxiv.org/abs/2102.06191), 2021

## C. Self-supervised / contrastive representation learning

26. M. Caron, P. Bojanowski, A. Joulin, M. Douze — "Deep Clustering for Unsupervised Learning of
    Visual Features (DeepCluster)," ECCV 2018
27. M. Caron, H. Touvron, I. Misra, et al. — "Emerging Properties in Self-Supervised Vision
    Transformers (DINO)," [arXiv:2104.14294](https://arxiv.org/abs/2104.14294), ICCV 2021
28. J.-B. Grill, F. Strub, F. Altché, et al. — "Bootstrap Your Own Latent (BYOL),"
    [arXiv:2006.07733](https://arxiv.org/abs/2006.07733), NeurIPS 2020
29. K. He, X. Chen, S. Xie, Y. Li, P. Dollár, R. Girshick — "Masked Autoencoders Are Scalable
    Vision Learners (MAE)," [arXiv:2111.06377](https://arxiv.org/abs/2111.06377), CVPR 2022
30. A. Dosovitskiy, L. Beyer, A. Kolesnikov, et al. — "An Image is Worth 16x16 Words:
    Transformers for Image Recognition at Scale (ViT)," [arXiv:2010.11929](https://arxiv.org/abs/2010.11929), ICLR 2021
31. K. He, X. Zhang, S. Ren, J. Sun — "Deep Residual Learning for Image Recognition (ResNet),"
    [arXiv:1512.03385](https://arxiv.org/abs/1512.03385), CVPR 2016

## D. Classical / probabilistic clustering and segmentation foundations

32. D. P. Kingma, M. Welling — "Auto-Encoding Variational Bayes,"
    [arXiv:1312.6114](https://arxiv.org/abs/1312.6114), ICLR 2014
33. J. Xie, R. Girshick, A. Farhadi — "Unsupervised Deep Embedding for Clustering Analysis
    (DEC)," [arXiv:1511.06335](https://arxiv.org/abs/1511.06335), ICML 2016
34. J. MacQueen — "Some Methods for Classification and Analysis of Multivariate Observations,"
    Proc. 5th Berkeley Symposium on Mathematical Statistics and Probability, 1967
35. P. Krähenbühl, V. Koltun — "Efficient Inference in Fully Connected CRFs with Gaussian Edge
    Potentials," NeurIPS 2011
36. P. F. Felzenszwalb, D. P. Huttenlocher — "Efficient Graph-Based Image Segmentation," IJCV,
    vol. 59, no. 2, 2004

## E. Discrete/generative latent representations

37. A. Razavi, A. van den Oord, O. Vinyals — "Generating Diverse High-Fidelity Images with
    VQ-VAE-2," [arXiv:1906.00446](https://arxiv.org/abs/1906.00446), NeurIPS 2019

## F. Remote sensing self-supervised learning & foundation models

38. Y. Cong, S. Khanna, C. Meng, et al. — "SatMAE: Pre-training Transformers for Temporal and
    Multi-Spectral Satellite Imagery," [arXiv:2207.08051](https://arxiv.org/abs/2207.08051), NeurIPS 2022
39. A. Chopra, P. K. Chhipa, G. Mengi, R. Gupta, M. Liwicki — "Domain Adaptable Self-Supervised
    Representation Learning on Remote Sensing Satellite Imagery," [arXiv:2304.09874](https://arxiv.org/abs/2304.09874), 2023
40. K. Ayush, et al. — "Self-Supervised Pretraining on Satellite Imagery: Label-Efficient
    Vehicle Detection," [arXiv:2210.11815](https://arxiv.org/abs/2210.11815), 2022
41. K. Chen, C. Liu, W. Chen, Z. Zhang, H. Li, Z. Zou, Z. Shi — "RSPrompter: Learning to Prompt
    for Remote Sensing Instance Segmentation Based on Visual Foundation Model," IEEE TGRS, 2024
42. L. P. Osco, J. Wu, et al. — "The Segment Anything Model (SAM) for Remote Sensing
    Applications: From Zero to One Shot," ISPRS J. Photogramm. Remote Sens., 2023

## G. Benchmark-scale evaluation and label-efficiency framing for RS SSL

43. "Evaluating the Label Efficiency of Contrastive Self-Supervised Learning for
    Multi-Resolution Satellite Imagery," [arXiv:2210.06786](https://arxiv.org/abs/2210.06786), 2022

