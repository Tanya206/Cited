# Evidence Review — golden dataset

43 answerable items still need evidence.

For each item: tick `[x]` if the quote supports the reference answer,
replace the quote text if it does not, or leave `[ ]` to flag it.

Quotes are verbatim from the indexed chunk named below and are
guaranteed to pass `python -m eval.validate_golden`.

## G01 — definition [ok]

**Q:** What is semantic segmentation?

**Reference answer:** In the FCN paper, semantic segmentation labels each pixel with the class of its enclosing object or region.

**Expected pages:** [1]

- **Reference 1  Long_Fully_Convolutional_Networks_2015_CVPR_paper** p.1 (coverage 0.7, `Reference 1  Long_Fully_Convolutional_Networks_2015_CVPR_paper_c0001`, verified=True)

  - [ ] `Prior approaches have used convnets for semantic segmentation [27, 2, 7, 28, 15, 13, 9], in which each pixel is labeled with the class of its enclosing object or region, but with short- comings that this work addresses.`

---

## G02 — method [ok]

**Q:** What is the central idea of fully convolutional networks for segmentation?

**Reference answer:** FCNs replace fully connected classification layers with convolutional layers so dense, pixel-wise predictions can be produced for arbitrary image sizes.

**Expected pages:** [1]

- **Reference 1  Long_Fully_Convolutional_Networks_2015_CVPR_paper** p.1 (coverage 0.33, `Reference 1  Long_Fully_Convolutional_Networks_2015_CVPR_paper_c0003`, verified=True)

  - [ ] `Fully convolutional networks can efficiently learn to make dense predictions for per-pixel tasks like semantic segmen- tation.`

---

## G04 — method [ok]

**Q:** What do atrous convolutions provide in DeepLab?

**Reference answer:** Atrous convolutions enlarge the receptive field without reducing feature-map resolution or increasing the number of parameters proportionally.

**Expected pages:** [1]

- **Reference 3 Atrous Convolution for Semantic Segmentation** p.1 (coverage 0.43, `Reference 3 Atrous Convolution for Semantic Segmentation_c0001`, verified=True)

  - [ ] `With atrous convo- lution, one is able to control the resolution at which feature 1 Conv kernel: 3x3 Conv kernel: 3x3 Conv kernel: 3x3 rate: 6 rate: 24 rate: 1 rate = 24 rate = 6 rate = 1 Feature map Feature map Feature map responses are computed within DCNNs without requiring learning extra parameters.`

---

## G05 — benchmark [ok]

**Q:** What kind of task does the Inria Aerial Image Labeling Benchmark evaluate?

**Reference answer:** It evaluates semantic labeling of aerial imagery, especially the ability of methods to generalize across different cities.

**Expected pages:** [1]

- **Reference 4 AerialImageLabelingDataset_4** p.1 (coverage 0.33, `Reference 4 AerialImageLabelingDataset_4_c0000`, verified=True)

  - [ ] `Can Semantic Labeling Methods Generalize to Any City?`

---

## G07 — method [ok]

**Q:** What are the main stages of spectral clustering?

**Reference answer:** Spectral clustering builds a similarity graph, computes a spectral embedding from a graph matrix, then clusters points in that embedding.

**Expected pages:** [1, 2]

- **Reference 6 spectral-clustering-analysis-and-an-algorithm-Paper** p.1 (coverage 0.3, `Reference 6 spectral-clustering-analysis-and-an-algorithm-Paper_c0000`, verified=True)

  - [ ] `Berkeley jordan@cs.berkeley.edu Abstract Despite many empirical successes of spectral clustering methods- algorithms that cluster points using eigenvectors of matrices de- rived from the data- there are several unresolved issues.`

---

## G08 — definition [LOW-COVERAGE]

**Q:** How does SimCLR learn representations without labels?

**Reference answer:** SimCLR contrasts two augmented views of the same image against views of other images to learn visual representations.

**Expected pages:** [1]

- **Reference 7 SimCLR Contrastive learning** p.1 (coverage 0.25, `Reference 7 SimCLR Contrastive learning_c0000`, verified=True)

  - [ ] `A Simple Framework for Contrastive Learning of Visual Representations Ting Chen 1 Simon Kornblith 1 Mohammad Norouzi 1 Geoffrey Hinton 1 Abstract This paper presents SimCLR: a simple framework for contrastive learning of visual representations.`

---

## G10 — method [ok]

**Q:** How does MoCo maintain a large set of negative keys?

**Reference answer:** MoCo uses a queue of encoded keys and updates its key encoder with a momentum update from the query encoder.

**Expected pages:** [1]

- **Reference 8_Momentum_Contrast_for_Unsupervised_Visual_Representation_Learning_CVPR_2020_paper** p.1 (coverage 0.55, `Reference 8_Momentum_Contrast_for_Unsupervised_Visual_Representation_Learning_CVPR_2020_paper_c0003`, verified=True)

  - [ ] `Momentum Contrast (MoCo) trains a visual represen- tation encoder by matching an encoded query q to a dictionary of encoded keys using a contrastive loss.`

---

## G11 — method [ok]

**Q:** What is SwAV contrasting during self-supervised learning?

**Reference answer:** SwAV contrasts cluster assignments of different augmented views instead of directly contrasting image features.

**Expected pages:** [1]

- **Reference 9 SwAV - Unsupervised learning of Visual features by contrasting cluster assignments** p.1 (coverage 0.67, `Reference 9 SwAV - Unsupervised learning of Visual features by contrasting cluster assignments_c0000`, verified=True)

  - [ ] `Specifically, our method simultaneously clusters the data while enforcing consistency between cluster assignments produced for different augmentations (or “views”) of the same image, instead of comparing features directly as in contrastive learning.`

---

## G12 — method [LOW-COVERAGE]

**Q:** How does VQ-VAE create discrete latent representations?

**Reference answer:** VQ-VAE maps encoder outputs to entries in a learned codebook and decodes the quantized latent representation.

**Expected pages:** [1]

- **Reference 10 VQVAE Neural Discrete Representational Learning** p.1 (coverage 0.27, `Reference 10 VQVAE Neural Discrete Representational Learning_c0000`, verified=True)

  - [ ] `Our model, the Vector Quantised- Variational AutoEncoder (VQ-VAE), differs from VAEs in two key ways: the encoder network outputs discrete, rather than continuous, codes; and the prior is learnt rather than static.`

---

## G13 — method [ok]

**Q:** What does SegSort use to produce semantic segments?

**Reference answer:** SegSort learns pixel embeddings and groups them through discriminative sorting of image segments.

**Expected pages:** [1]

- **Reference 12 SegSort** p.1 (coverage 0.36, `Reference 12 SegSort_c0000`, verified=True)

  - [ ] `SegSort: Segmentation by Discriminative Sorting of Segments Jyh-Jing Hwang1,2 Stella X.`

---

## G14 — application [ok]

**Q:** What does unsupervised single-scene semantic segmentation aim to do for Earth observation?

**Reference answer:** It aims to discover meaningful semantic regions in a single Earth-observation image without ground-truth labels.

**Expected pages:** [1]

- **Reference 13 Unsupervised_Single-Scene_Semantic_Segmentation_fo (1)** p.1 (coverage 0.31, `Reference 13 Unsupervised_Single-Scene_Semantic_Segmentation_fo (1)_c0000`, verified=True)

  - [ ] `60, 2022 5228011 Unsupervised Single-Scene Semantic Segmentation for Earth Observation Sudipan Saha , Member, IEEE, Muhammad Shahzad, Lichao Mou , Qian Song , Member, IEEE, and Xiao Xiang Zhu , Fellow, IEEE Abstract—Earth observation data have huge potential to enrich our knowledge about our planet.`

---

## G15 — method [LOW-COVERAGE]

**Q:** What does Segment Anything produce from prompts?

**Reference answer:** Segment Anything predicts object masks from prompts such as points, boxes, masks, or text-related inputs.

**Expected pages:** [1]

- **Reference 15 2023_Segment_Anything_2304.02643v1** p.1 (coverage 0.27, `Reference 15 2023_Segment_Anything_2304.02643v1_c0000`, verified=True)

  - [ ] `We are releasing the Segment Anything Model (SAM) and cor- responding dataset (SA-1B) of 1B masks and 11M images at https://segment-anything.com to foster research into foun- dation models for computer vision.`

---

## G16 — application [ok]

**Q:** Why are superpixels useful for unsupervised hyperspectral image segmentation?

**Reference answer:** Superpixels group locally coherent pixels, reducing noise and providing spatial units for clustering hyperspectral information.

**Expected pages:** [1]

- **Reference 16 2024_Unsupervised_Segmentation_of_Hyperspectral_Remote_sensing_Satellite_images_with_Superpixels2204.12296v2** p.1 (coverage 0.31, `Reference 16 2024_Unsupervised_Segmentation_of_Hyperspectral_Remote_sensing_Satellite_images_with_Superpixels2204.12296v2_c0000`, verified=True)

  - [ ] `The method exploits the mean-shift clustering algorithm that takes as input a preliminary hyperspectral superpixels segmentation together with the spectral pixel information.`

---

## G17 — application [ok]

**Q:** What does the 2025 urban satellite-imagery clustering study seek to reveal?

**Reference answer:** It uses unsupervised deep clustering of high-resolution satellite imagery to reveal phenotypes of urban development in Sub-Saharan Africa.

**Expected pages:** [1]

- **Reference 17 2025_Unsupervised deep clustering of high-resolution satellite imagery reveals** p.1 (coverage 0.87, `Reference 17 2025_Unsupervised deep clustering of high-resolution satellite imagery reveals_c0001`, verified=True)

  - [ ] `A R T I C L E I N F O A B S T R A C T Editor: Evgenios Agathokleous https://doi.org/10.1016/j.scitotenv.2025.179739 Received 15 February 2025; Received in revised form 19 May 2025; Accepted 21 May 2025 Unsupervised deep clustering of high-resolution satellite imagery reveals phenotypes of urban development in Sub-Saharan Africa A.`

---

## G18 — method [ok]

**Q:** What is the main idea behind SLIC superpixels?

**Reference answer:** SLIC adapts k-means clustering in a combined color and image-space domain to efficiently produce compact superpixels.

**Expected pages:** [1]

- **Reference 18 SLIC** p.1 (coverage 0.46, `Reference 18 SLIC_c0000`, verified=True)

  - [ ] `We introduce a novel algorithm that clusters pixels in the combined five-dimensional color and image plane space to effi- ciently generate compact, nearly uniform superpixels.`

---

## G19 — method [ok]

**Q:** What does Invariant Information Clustering optimize?

**Reference answer:** IIC maximizes mutual information between cluster assignments of paired transformed inputs.

**Expected pages:** [1]

- **1807.06653v4** p.1 (coverage 0.4, `1807.06653v4_c0001`, verified=True)

  - [ ] `The objective is simply to maximise mutual information between the class assignments of each pair.`

---

## G20 — method [ok]

**Q:** How does PiCIE use invariance and equivariance?

**Reference answer:** PiCIE learns unsupervised semantic segmentation by encouraging invariance to photometric changes and equivariance to geometric transformations during clustering.

**Expected pages:** [1]

- **2103.17070v1** p.1 (coverage 0.43, `2103.17070v1_c0001`, verified=True)

  - [ ] `Recent progress in self- PiCIE: Unsupervised Semantic Segmentation using Invariance and Equivariance Jang Hyun Cho1 Utkarsh Mall2 Kavita Bala2 Bharath Hariharan2`

---

## G21 — method [ok]

**Q:** What is STEGO distilled from?

**Reference answer:** STEGO distills feature correspondences from self-supervised visual features to obtain unsupervised semantic segmentation.

**Expected pages:** [1]

- **2203.08414v1** p.1 (coverage 0.58, `2203.08414v1_c0000`, verified=True)

  - [ ] `This observation motivates us to design STEGO (Self-supervised Transformer with Energy-based Graph Optimization), a novel framework that distills unsupervised features into high- quality discrete semantic labels.`

---

## G22 — method [LOW-COVERAGE]

**Q:** How does W-Net support fully unsupervised image segmentation?

**Reference answer:** W-Net uses a two-part encoder-decoder architecture that jointly learns a soft segmentation and reconstructs the input image without labels.

**Expected pages:** [1]

- **1711.08506v1** p.1 (coverage 0.25, `1711.08506v1_c0002`, verified=True)

  - [ ] `The first FCN encodes an input image, using fully convolutional layers, into a k-way soft segmentation.`

---

## G23 — method [ok]

**Q:** What is differentiable feature clustering used for in unsupervised image segmentation?

**Reference answer:** It jointly learns pixel features and cluster assignments through a differentiable clustering objective without semantic labels.

**Expected pages:** [1]

- **2007.09990v1** p.1 (coverage 0.38, `2007.09990v1_c0003`, verified=True)

  - [ ] `Driven by the high feature descriptiveness of CNNs, a joint learning approach is presented that predicts, for an arbitrary image input, unknown cluster labels and learns the optimal CNN parameters for the image pixel clustering.`

---

## G24 — method [LOW-COVERAGE]

**Q:** What is the central assumption behind SCAN?

**Reference answer:** SCAN assumes that semantically similar images should receive the same cluster assignment and learns from nearest-neighbor consistency.

**Expected pages:** [1]

- **2005.12320v2** p.1 (coverage 0.15, `2005.12320v2_c0000`, verified=True)

  - [ ] `SCAN: Learning to Classify Images without Labels Wouter Van Gansbeke1⋆ Simon Vandenhende1⋆ Stamatios Georgoulis2 Marc Proesmans1 Luc Van Gool1,2 1KU Leuven/ESAT-PSI 2ETH Zurich/CVL, TRACE arXiv:2005.12320v2 [cs.CV] 3 Jul 2020 Abstract.`

---

## G25 — method [ok]

**Q:** What does unsupervised semantic segmentation by contrasting object mask proposals use as supervision?

**Reference answer:** It uses object mask proposals to construct contrastive learning signals without semantic labels.

**Expected pages:** [1]

- **2102.06191v3** p.1 (coverage 0.45, `2102.06191v3_c0000`, verified=True)

  - [ ] `Unsupervised Semantic Segmentation by Contrasting Object Mask Proposals Wouter Van Gansbeke1* Simon Vandenhende1* Stamatios Georgoulis2 Luc Van Gool1,2 1KU Leuven/ESAT-PSI 2ETH Zurich/CVL, TRACE Abstract arXiv:2102.06191v3 [cs.CV] 3 Aug 2021 Being able to learn dense semantic representations of images without supervision is an important problem in com- puter vision.`

---

## G26 — method [ok]

**Q:** What does DeepCluster alternate between during training?

**Reference answer:** DeepCluster alternates between clustering image features and using the resulting cluster assignments as pseudo-labels for representation learning.

**Expected pages:** [1]

- **1807.05520v2** p.1 (coverage 0.36, `1807.05520v2_c0000`, verified=True)

  - [ ] `In this work, we present DeepCluster, a clus- tering method that jointly learns the parameters of a neural network and the cluster assignments of the resulting features.`

---

## G27 — method [LOW-COVERAGE]

**Q:** What is the teacher-student mechanism in DINO?

**Reference answer:** DINO trains a student network to match the output distribution of a teacher network updated with an exponential moving average of the student.

**Expected pages:** [1]

- **2104.14294v2** p.1 (coverage 0.08, `2104.14294v2_c0000`, verified=True)

  - [ ] `We implement our findings into a simple self-supervised method, called DINO, which we interpret as a form of self-distillation with no labels.`

---

## G28 — comparison [ok]

**Q:** How does BYOL avoid using negative pairs?

**Reference answer:** BYOL trains an online network to predict the representation of a slowly updated target network, so it does not require explicit negative pairs.

**Expected pages:** [1]

- **2006.07733v3** p.1 (coverage 0.38, `2006.07733v3_c0001`, verified=True)

  - [ ] `From an augmented view of an image, we train the online network to predict the target network representation of the same image under a different augmented view.`

---

## G29 — method [ok]

**Q:** What is the pretext task in masked autoencoders?

**Reference answer:** MAE masks a large portion of image patches and learns to reconstruct the missing pixels from the visible patches.

**Expected pages:** [1]

- **2111.06377v3** p.1 (coverage 0.55, `2111.06377v3_c0000`, verified=True)

  - [ ] `Our MAE approach is simple: we mask random patches of the input image and reconstruct the missing pixels.`

---

## G30 — definition [LOW-COVERAGE]

**Q:** How does a Vision Transformer represent an image?

**Reference answer:** ViT splits an image into fixed-size patches, linearly embeds them as tokens, and processes the token sequence with a Transformer.

**Expected pages:** [1]

- **2010.11929v2** p.1 (coverage 0.21, `2010.11929v2_c0000`, verified=True)

  - [ ] `We show that this reliance on CNNs is not necessary and a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks.`

---

## G31 — method [ok]

**Q:** What problem do residual connections address in ResNet?

**Reference answer:** Residual connections address the degradation problem in very deep networks by learning residual functions through shortcut connections.

**Expected pages:** [1]

- **1512.03385v1** p.1 (coverage 0.33, `1512.03385v1_c0000`, verified=True)

  - [ ] `Deep Residual Learning for Image Recognition Kaiming He Xiangyu Zhang Shaoqing Ren Jian Sun Microsoft Research {kahe, v-xiangz, v-shren, jiansun}@microsoft.com arXiv:1512.03385v1 [cs.CV] 10 Dec 2015 Abstract Deeper neural networks are more difficult to train.`

---

## G32 — method [LOW-COVERAGE]

**Q:** What does a variational autoencoder optimize?

**Reference answer:** A VAE optimizes a variational lower bound that balances reconstruction quality with a regularized latent distribution.

**Expected pages:** [1]

- **1312.6114v11** p.1 (coverage 0.27, `1312.6114v11_c0000`, verified=True)

  - [ ] `First, we show that a reparameterization of the variational lower bound yields a lower bound estimator that can be straightforwardly optimized using stan- dard stochastic gradient methods.`

---

## G33 — method [ok]

**Q:** What does Deep Embedded Clustering optimize after initialization?

**Reference answer:** DEC refines an embedding and cluster centroids by minimizing divergence between soft assignments and an auxiliary target distribution.

**Expected pages:** [1]

- **1511.06335v2** p.1 (coverage 0.38, `1511.06335v2_c0002`, verified=True)

  - [ ] `Instead we propose to iteratively refine clusters with an auxiliary target distribution derived from the current soft cluster assignment.`

---

## G34 — definition [ok]

**Q:** What is the objective of k-means clustering?

**Reference answer:** MacQueen frames k-means as constructing partitions that are efficient in terms of within-class variance.

**Expected pages:** [1]

- **macqueen** p.1 (coverage 0.6, `macqueen_c0000`, verified=True)

  - [ ] `The process, which is called 'k-means,' appears to give partitions which are reasonably efficient in the sense of within-class variance.`

---

## G35 — method [LOW-COVERAGE]

**Q:** Why are fully connected CRFs difficult to use directly for image labeling?

**Reference answer:** They connect all pixel pairs, creating an enormous inference problem that requires an efficient approximation.

**Expected pages:** [1]

- **1210.5644v1** p.1 (coverage 0.18, `1210.5644v1_c0000`, verified=True)

  - [ ] `Efficient Inference in Fully Connected CRFs with Gaussian Edge Potentials Philipp Kr ̈ahenb ̈uhl Computer Science Department Stanford University philkr@cs.stanford.edu arXiv:1210.5644v1 [cs.CV] 20 Oct 2012 Abstract Most state-of-the-art techniques for multi-class image segmentation and labeling use conditional random fields defined over pixels or image regions.`

---

## G36 — method [LOW-COVERAGE]

**Q:** What graph property does efficient graph-based image segmentation use to decide whether to merge regions?

**Reference answer:** It compares inter-region edge differences with each component's internal variation using a scale-dependent threshold.

**Expected pages:** [1]

- **efficient-graph-based-image-segmentation-tyi8hqdokm** p.1 (coverage 0.08, `efficient-graph-based-image-segmentation-tyi8hqdokm_c0000`, verified=True)

  - [ ] `For instance intermediate-level vision prob- lems such as stereo and motion estimation require an appropriate region of support for correspondence oper- ations.`

---

## G37 — method [ok]

**Q:** What is VQ-VAE-2 designed to improve over VQ-VAE?

**Reference answer:** VQ-VAE-2 uses a hierarchical discrete latent architecture to generate more diverse, higher-fidelity images.

**Expected pages:** [1]

- **1906.00446v1** p.1 (coverage 0.36, `1906.00446v1_c0000`, verified=True)

  - [ ] `Generating Diverse High-Fidelity Images with VQ-VAE-2 Ali Razavi∗ DeepMind alirazavi@google.com Aäron van den Oord∗ DeepMind avdnoord@google.com arXiv:1906.00446v1 [cs.LG] 2 Jun 2019 Abstract We explore the use of Vector Quantized Variational AutoEncoder (VQ-VAE) models for large scale image generation.`

---

## G38 — application [ok]

**Q:** What kinds of satellite information does SatMAE pre-train on?

**Reference answer:** SatMAE pre-trains Transformers for temporal and multispectral satellite imagery.

**Expected pages:** [1]

- **2207.08051v3** p.1 (coverage 0.75, `2207.08051v3_c0000`, verified=True)

  - [ ] `SatMAE: Pre-training Transformers for Temporal and Multi-Spectral Satellite Imagery Yezhen Cong∗ yzcong@stanford.edu Samar Khanna∗ samar.khanna@stanford.edu arXiv:2207.08051v3 [cs.CV] 15 Jan 2023 Erik Rozi Yutong He Marshall Burke David B.`

---

## G41 — comparison [LOW-COVERAGE]

**Q:** How do SimCLR and MoCo differ in handling negative examples?

**Reference answer:** SimCLR commonly relies on negatives from the current batch, whereas MoCo maintains a queue of keys and a momentum encoder to supply a large, consistent dictionary.

**Expected pages:** [1]

- **Reference 7 SimCLR Contrastive learning** p.1 (coverage 0.06, `Reference 7 SimCLR Contrastive learning_c0000`, verified=True)

  - [ ] `A Simple Framework for Contrastive Learning of Visual Representations Ting Chen 1 Simon Kornblith 1 Mohammad Norouzi 1 Geoffrey Hinton 1 Abstract This paper presents SimCLR: a simple framework for contrastive learning of visual representations.`

- **Reference 8_Momentum_Contrast_for_Unsupervised_Visual_Representation_Learning_CVPR_2020_paper** p.1 (coverage 0.29, `Reference 8_Momentum_Contrast_for_Unsupervised_Visual_Representation_Learning_CVPR_2020_paper_c0003`, verified=True)

  - [ ] `Momentum Contrast (MoCo) trains a visual represen- tation encoder by matching an encoded query q to a dictionary of encoded keys using a contrastive loss.`

---

## G42 — comparison [LOW-COVERAGE]

**Q:** How do SimCLR and BYOL differ in their use of negative pairs?

**Reference answer:** SimCLR uses contrastive negative pairs, while BYOL learns by predicting a target-network representation and does not require explicit negatives.

**Expected pages:** [1]

- **Reference 7 SimCLR Contrastive learning** p.1 (coverage 0.13, `Reference 7 SimCLR Contrastive learning_c0000`, verified=True)

  - [ ] `A Simple Framework for Contrastive Learning of Visual Representations Ting Chen 1 Simon Kornblith 1 Mohammad Norouzi 1 Geoffrey Hinton 1 Abstract This paper presents SimCLR: a simple framework for contrastive learning of visual representations.`

- **2006.07733v3** p.1 (coverage 0.27, `2006.07733v3_c0001`, verified=True)

  - [ ] `While state-of-the art methods rely on negative pairs, BYOL achieves a new state of the art without them.`

---

## G43 — comparison [LOW-COVERAGE]

**Q:** How do FCN and U-Net both support dense prediction?

**Reference answer:** Both are fully convolutional and combine coarse semantic features with fine high-resolution ones through skip connections; FCN sums upsampled features, while U-Net concatenates them along a symmetric expanding path.

**Expected pages:** [1, 2]

- **Reference 1  Long_Fully_Convolutional_Networks_2015_CVPR_paper** p.1 (coverage 0.17, `Reference 1  Long_Fully_Convolutional_Networks_2015_CVPR_paper_c0000`, verified=True)

  - [ ] `Fully Convolutional Networks for Semantic Segmentation Jonathan Long∗ Evan Shelhamer∗ Trevor Darrell UC Berkeley {jonlong,shelhamer,trevor}@cs.berkeley.edu Abstract Convolutional networks are powerful visual models that yield hierarchies of features.`

- **Reference 2 U Net** p.2 (coverage 0.21, `Reference 2 U Net_c0002`, verified=True)

  - [ ] `In order to localize, high resolution features from the contracting path are combined with the upsampled 64 128 64 2 output segmentation map 1962 392 x 392 390 x 390 388 x 388 388 x 388 256 128 1002 2002 1982 512 256`

---

## G44 — comparison [LOW-COVERAGE]

**Q:** How do PiCIE and STEGO approach unsupervised semantic segmentation differently?

**Reference answer:** PiCIE learns clustering with invariance and equivariance constraints, whereas STEGO distills feature correspondences from pretrained self-supervised representations.

**Expected pages:** [1]

- **2103.17070v1** p.1 (coverage 0.33, `2103.17070v1_c0000`, verified=True)

  - [ ] `Our method, PiCIE (Pixel-level feature Clustering using Invariance and Equivariance), is the first method capable of segmenting both things and stuff categories without any hyperparam- eter tuning or task-specific pre-processing.`

- **2203.08414v1** p.1 (coverage 0.27, `2203.08414v1_c0000`, verified=True)

  - [ ] `This observation motivates us to design STEGO (Self-supervised Transformer with Energy-based Graph Optimization), a novel framework that distills unsupervised features into high- quality discrete semantic labels.`

---

## G45 — comparison [LOW-COVERAGE]

**Q:** How does MAE differ from SimCLR as a self-supervised learning objective?

**Reference answer:** MAE reconstructs masked image content, while SimCLR contrasts representations of augmented image views.

**Expected pages:** [1]

- **2111.06377v3** p.1 (coverage 0.18, `2111.06377v3_c0000`, verified=True)

  - [ ] `Masked Autoencoders Are Scalable Vision Learners ∗equal technical contribution †project lead Facebook AI Research (FAIR) Abstract arXiv:2111.06377v3 [cs.CV] 19 Dec 2021 This paper shows that masked autoencoders (MAE) are scalable self-supervised learners for computer vision.`

- **Reference 7 SimCLR Contrastive learning** p.1 (coverage 0.18, `Reference 7 SimCLR Contrastive learning_c0000`, verified=True)

  - [ ] `A Simple Framework for Contrastive Learning of Visual Representations Ting Chen 1 Simon Kornblith 1 Mohammad Norouzi 1 Geoffrey Hinton 1 Abstract This paper presents SimCLR: a simple framework for contrastive learning of visual representations.`

---

## G46 — numeric [ok]

**Q:** What ImageNet top-1 accuracy does the SimCLR paper report for its best model under linear evaluation?

**Reference answer:** The SimCLR paper reports 76.5% ImageNet top-1 accuracy under linear evaluation for its best model.

**Expected pages:** [1]

- **Reference 7 SimCLR Contrastive learning** p.1 (coverage 0.27, `Reference 7 SimCLR Contrastive learning_c0000`, verified=True)

  - [ ] `A linear classifier trained on self-supervised representations learned by Sim- CLR achieves 76.5% top-1 accuracy, which is a 7% relative improvement over previous state-of- the-art, matching the performance of a supervised ResNet-50.`

---

## G47 — numeric [ok]

**Q:** What fraction of image patches does MAE mask in its asymmetric encoder-decoder design?

**Reference answer:** MAE masks 75% of image patches.

**Expected pages:** [1]

- **2111.06377v3** p.1 (coverage 0.5, `2111.06377v3_c0003`, verified=True)

  - [ ] `During pre-training, a large random subset of image patches (e.g., 75%) is masked out.`

---

## G48 — numeric [ok]

**Q:** What patch size is named in the title of the Vision Transformer paper?

**Reference answer:** The title names 16x16 image patches.

**Expected pages:** [1]

- **2010.11929v2** p.1 (coverage 0.4, `2010.11929v2_c0001`, verified=True)

  - [ ] `1 INTRODUCTION 1 AN IMAGE IS WORTH 16X16 WORDS: TRANSFORMERS FOR IMAGE RECOGNITION AT SCALE Self-attention-based architectures, in particular Transformers (Vaswani et al., 2017), have become the model of choice in natural language processing (NLP).`

---
