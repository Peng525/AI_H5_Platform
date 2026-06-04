# 横评记录 20260531-deepseek-v4-pro-学术-phase1

## 基本信息

| 字段 | 值 |
|------|-----|
| 日期 | 20260531 |
| active_profile | deepseek-v4-pro |
| benchmark_phase | 1 |
| 类型 | 学术 |
| ppt-master 项目路径 | E:\cursor projects\类ppt 小程序\develop\ppt-master-main\projects\benchmark-deepseek-v4-pro-学术-20260531 |
| exports 路径 | - |
| 总耗时（分钟） | 19.9 |
| 实际页数 | 6 |

**错误**: 05_method.svg: The read operation timed out; 06_experiment.svg: [WinError 10054] 远程主机强迫关闭了一个现有的连接。; svg_to_pptx failed: Traceback (most recent call last):
  File "E:\cursor projects\��ppt С����\develop\ppt-master-main\skills\ppt-master\scripts\svg_to_pptx.py", line 17, in <module>
    main()
    ~~~~^^
  File "E:\cursor projects\��ppt С����\develop\ppt-master-main\skills\ppt-master\scripts\svg_to_pptx\pptx_cli.py", line 522, in main
    ok = create_pptx_with_native_svg(
        output_path=native_path,
    ...<6 lines>...
        **shared_kwargs,
    )
  File "E:\cursor projects\��ppt С����\develop\ppt-master-main\skills\ppt-master\scripts\svg_to_pptx\pptx_builder.py", line 505, in create_pptx_with_native_svg
    convert_svg_to_slide_shapes(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        svg_path, slide_num=slide_num, verbose=verbose,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        merge_paragraph

## Phase 1 评分（1–5）

| 维度 | 分 | 备注 |
|------|-----|------|
| **核心均分 (1–6)** | **0** | |

## 成本与问题

| 字段 | 值 |
|------|-----|
| 预估 API 费用（USD） | $0.1102 |
| 耗时评分 |  |

---
*由 develop/scripts/ppt_benchmark/run_phase1.py 自动生成*