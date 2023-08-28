import rasterio
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from rasterio.warp import reproject, Resampling

'''
This function downscales SMAP data using Random Forest Regression. 
It takes in a folder of predictor rasters and a SMAP raster, and outputs a downscaled SMAP raster.

Inputs:
    predictor_folder: Folder containing predictor rasters
    smap_path: Path to SMAP raster

Outputs:
    downscale_raster: Downscaled SMAP raster

'''

def downscaler(predictor_folder, smap_path):
    
    print('\nProcessing ...')
    # Open and read raster files
    with rasterio.open(smap_path) as src_smap:
        smap_data = src_smap.read(1)
        smap_profile = src_smap.profile

    reprojected_predictors = []
    all_files = os.listdir(predictor_folder)
    predictor_paths = [os.path.join(predictor_folder, filename) for filename in all_files if filename.lower().endswith(".tif")]

    for predictor_path in predictor_paths:
        with rasterio.open(predictor_path) as src_predictor:
            predictor_data = src_predictor.read(1)
            
            # Reproject predictor data to match SMAP shape
            reprojected_data = np.empty_like(smap_data)
            reproject(predictor_data, reprojected_data,
                      src_transform = src_predictor.transform,
                      src_crs = src_predictor.crs,
                      dst_transform = smap_profile["transform"],
                      dst_crs = smap_profile["crs"],
                      resampling = Resampling.bilinear)
            
            reprojected_predictors.append(reprojected_data)

    # Stack reprojected predictor bands
    stacked_predictors = np.stack(reprojected_predictors, axis = 0)

    # Reshape predictor data to DataFrame
    num_bands, height, width = stacked_predictors.shape
    predictors_df = pd.DataFrame(stacked_predictors.reshape(num_bands, -1).T,
                                 columns = [f"predictor_{i}" for i in range(num_bands)])
    
    # Flatten SMAP data
    smap_values = smap_data.flatten()
    
    # Create combined DataFrame
    combined_data = pd.concat([predictors_df, pd.Series(smap_values, name = "smap")], axis = 1)
    
    # Split data into train and test sets
    np.random.seed(123)
    train_indices = np.random.choice(combined_data.shape[0], int(0.8 * combined_data.shape[0]), replace = False)
    train_data = combined_data.iloc[train_indices]
    test_data = combined_data.drop(train_indices)
    
    # Impute missing values in numeric columns using mean of training data
    numeric_cols = train_data.select_dtypes(include = [np.number]).columns
    train_data[numeric_cols] = train_data[numeric_cols].fillna(train_data[numeric_cols].mean())
    test_data[numeric_cols] = test_data[numeric_cols].fillna(train_data[numeric_cols].mean())
    
    # Train the Random Forest Regression model
    X_train = train_data.drop("smap", axis = 1)
    y_train = train_data["smap"]
    rfr_model = RandomForestRegressor(random_state = 0)
    rfr_model.fit(X_train, y_train)
    
    # Make predictions using the trained model
    downscale_predictions = rfr_model.predict(predictors_df)

    # Reshape predictions to match the original raster shape
    downscale_raster = downscale_predictions.reshape(height, width)

    # Write the output raster
    output_path = os.path.join(os.path.dirname(smap_path), 'downscaled.TIF')
    with rasterio.open(output_path, "w", **smap_profile) as dst:
        dst.write(downscale_raster, 1)

    print('Processing ... Done.')
    return downscale_raster

# How to use the function
predictor_folder = input("Enter the path to the folder containing predictor rasters (e.g. /Users/username/Desktop/predictors): ")
smap_path = input("Enter the path to the SMAP raster (e.g. /Users/username/Desktop/smap.tif): ")
array = downscaler(predictor_folder, smap_path)
