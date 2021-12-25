#common
N_VIEWS=9
work_dir="results/neural_recon"
distributed=True
dist_params = dict(backend='nccl')
checkpoint_config = dict(interval=1)
log_level = 'INFO'
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])
resume_from = None
load_from = None



#data
dataset_type = 'ScanNetDataset'
img_norm_cfg = dict(
    mean=[103.53, 116.28, 123.675], std=[1.0, 1.0, 1.0], to_rgb=False)
train_pipeline = [
    dict(type='SeqResizeImage', size=(640,480)),
    dict(type='SeqToTensor'),#in sequence, we need to tensor first 
    dict(type='SeqRandomTransformSpace', voxel_dim=[96, 96, 96], voxel_size=0.04, random_rotation=True, random_translation=True,
                 paddingXY=0.1, paddingZ=0.025, max_epoch=991),
    dict(type='SeqIntrinsicsPoseToProjection', n_views=N_VIEWS, stride=4),
    dict(type='SeqNormalizeImages', **img_norm_cfg),
    dict(type='Collect', keys=['imgs','depth','intrinsics','extrinsics', 'tsdf_list_full', 'proj_matrices', 
            'vol_origin_partial', 'world_to_aligned_camera','tsdf_list','occ_list'], meta_keys=['fragment','scene']),
    #dict(type='')
]
test_pipeline = []
use_data_loaders=True
data = dict(
    samples_per_gpu=1,
    workers_per_gpu=4,
    train=dict(
            type=dataset_type,
            datapath='/media/achao/Innov8/database/scannet-download',
            mode='train_debug',
            nviews=N_VIEWS, 
            n_scales=2,
            pipeline=train_pipeline),
    val=dict(pipeline=test_pipeline))

# model settings
model = dict(
    type='NeuralRecon',
    model_cfgs=dict(
        N_LAYER=3,
        N_VOX=[96, 96, 96],
        VOXEL_SIZE=0.04,
        TRAIN_NUM_SAMPLE=[4096, 16384, 65536],
        TEST_NUM_SAMPLE=[4096, 16384, 65536],
        BACKBONE2D=dict(
            ARC='fpn-mnas-1'),
        FUSION=dict(
            FUSION_ON=True,
            HIDDEN_DIM=64,
            AVERAGE=False,
            FULL=True),
        LW=[1.0, 0.8, 0.64],
        THRESHOLDS=[0, 0, 0],
        POS_WEIGHT=1.5,
        SPARSEREG=dict(DROPOUT=False)
    )
)


##runner settings

optimizer_config = dict(grad_clip=1.0)
lr_config = dict(
    policy='step',
    gamma=0.5,
    step=[12,24,48])
workflow = [('train', 1)]
runner = dict(
    type='EpochBasedRunner', 
    runner_cfgs=dict(
        optimizer = dict(type='Adam',lr=0.001, betas=(0.9, 0.999), weight_decay=0.0),
        max_epochs=991))