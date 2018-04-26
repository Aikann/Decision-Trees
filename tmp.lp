\ENCODING=ISO-8859-1
\Problem name: 

Minimize
 obj: row_error_0 + row_error_1 + row_error_2 + row_error_3 + row_error_4
Subject To
 constraint_15_0_0_0: 5 node_feature_0_0 - node_constant_0 - segment_leaf_0_0
                      + 2 segment_leaf_1_0 - segment_leaf_1_1
                      + 2 segment_leaf_2_0 + 2 segment_leaf_2_1 <= 5
 constraint_15_1_0_0: 5 node_feature_0_1 - node_constant_0 - segment_leaf_0_0
                      + 2 segment_leaf_1_0 - segment_leaf_1_1
                      + 2 segment_leaf_2_0 + 2 segment_leaf_2_1 <= 5
 constraint_16_0_0_1: 5 node_feature_0_0 + node_constant_0 + 2 segment_leaf_1_0
                      - segment_leaf_1_1 + 2 segment_leaf_2_0
                      + 2 segment_leaf_2_1 <= 5
 constraint_16_1_0_1: 5 node_feature_0_1 + node_constant_0 + 2 segment_leaf_1_0
                      - segment_leaf_1_1 + 2 segment_leaf_2_0
                      + 2 segment_leaf_2_1 <= 5
 constraint_17_0:     segment_leaf_0_0 + segment_leaf_1_1 + segment_leaf_2_1
                       = 1
 constraint_17_1:     segment_leaf_0_1 + segment_leaf_1_0 + segment_leaf_2_1
                       = 1
 constraint_17_2:     segment_leaf_0_1 + segment_leaf_1_0 + segment_leaf_2_1
                       = 1
 constraint_17_3:     segment_leaf_0_1 + segment_leaf_1_0 + segment_leaf_2_1
                       = 1
 constraint_17_4:     segment_leaf_0_1 + segment_leaf_1_0 + segment_leaf_2_0
                       = 1
 constraint_18_0:     segment_leaf_0_0 + segment_leaf_1_0 + segment_leaf_2_0
                       = 1
 constraint_18_1:     segment_leaf_0_1 + segment_leaf_1_1 + segment_leaf_2_1
                       = 1
 constraint_19_0_0:   prediction_type_1_0 - row_error_0 + segment_leaf_0_0 <= 1
 constraint_19_0_1:   prediction_type_1_1 - row_error_0 + segment_leaf_1_1
                      + segment_leaf_2_1 <= 1
 constraint_19_1_0:   prediction_type_0_0 - row_error_1 + segment_leaf_1_0 <= 1
 constraint_19_1_1:   prediction_type_0_1 - row_error_1 + segment_leaf_0_1
                      + segment_leaf_2_1 <= 1
 constraint_19_2_0:   prediction_type_1_0 - row_error_2 + segment_leaf_1_0 <= 1
 constraint_19_2_1:   prediction_type_1_1 - row_error_2 + segment_leaf_0_1
                      + segment_leaf_2_1 <= 1
 constraint_19_3_0:   prediction_type_1_0 - row_error_3 + segment_leaf_1_0 <= 1
 constraint_19_3_1:   prediction_type_1_1 - row_error_3 + segment_leaf_0_1
                      + segment_leaf_2_1 <= 1
 constraint_19_4_0:   prediction_type_0_0 - row_error_4 + segment_leaf_1_0
                      + segment_leaf_2_0 <= 1
 constraint_19_4_1:   prediction_type_0_1 - row_error_4 + segment_leaf_0_1 <= 1
 constraint_20_0:     prediction_type_0_0 + prediction_type_1_0  = 1
 constraint_20_1:     prediction_type_0_1 + prediction_type_1_1  = 1
 constraint_21_0:     node_feature_0_0 + node_feature_0_1  = 1
Bounds
 0 <= node_feature_0_0 <= 1
 0 <= node_feature_0_1 <= 1
-1 <= node_constant_0 <= 4
 0 <= prediction_type_0_0 <= 1
 0 <= prediction_type_1_0 <= 1
 0 <= prediction_type_0_1 <= 1
 0 <= prediction_type_1_1 <= 1
 0 <= row_error_0 <= 1
 0 <= row_error_1 <= 1
 0 <= row_error_2 <= 1
 0 <= row_error_3 <= 1
 0 <= row_error_4 <= 1
 0 <= segment_leaf_0_0 <= 1
 0 <= segment_leaf_0_1 <= 1
 0 <= segment_leaf_1_0 <= 1
 0 <= segment_leaf_1_1 <= 1
 0 <= segment_leaf_2_0 <= 1
 0 <= segment_leaf_2_1 <= 1
End
