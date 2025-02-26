import cv2
import numpy as np
#from ultralytics import YOLO
import matplotlib.patches as patches
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from sahi import AutoDetectionModel
from sahi.predict import get_prediction
from sahi.predict import get_sliced_prediction
import os
import xml.etree.ElementTree as ET
import gpxpy
import gpxpy.gpx



def get_frame_at_timestamp(video_path, timestamp):
    """
    Video path relative video path to mp4 file
    Time stamp in seconds
    """
    
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC,(timestamp*1000))
        success, image = cap.read()
        print(success)
        if success:
            cv2.imwrite("dash_videos/Bancroft_Vid_2/Frame_Images/frame%d.jpg" % timestamp, image)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def train_YOLO_model():
    return

def extract_coordinates(filepath):
    output = []
    try:
        with open(filepath, 'r') as file:
            for line in file:
                bounds = line.split()
                try:
                    bounds = [float(bound) for bound in bounds]
                    output.append(bounds[1:])
                except Exception:
                    print(f"Error: File in incorrect format at {filepath}")
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return output
                
def plot_Bounding_Box(image_filepath, bounds):
    img = mpimg.imread(image_filepath)
    height, width, channels = img.shape
    imgplot = plt.imshow(img)
    ax = plt.subplot()
    for pos in bounds:
        print(pos)
        bottom_left_x_norm = pos[0] - (pos[2]/2)
        bottom_left_y_norm = pos[1] - (pos[3]/2)    
        rect = patches.Rectangle((int(round(bottom_left_x_norm * width)), int(round(bottom_left_y_norm * height))), int(round(pos[2] * width)), 
                                 int(round(pos[3]*height)), linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
    plt.show()
    
def train_YOLO_model(yaml_path):
    model = YOLO('yolo11n.pt')

    model.train(data="cone_dataset/traffic_cone.yaml", epochs=10, imgsz=640, batch=12)
    metrics = model.val()
    print(metrics)
    
def run_YOLO_frame(model_path):
    detection_model = AutoDetectionModel.from_pretrained(
        model_type="ultralytics",
        model_path=model_path,
        confidence_threshold=0.6,
        device="cpu",  # or 'cuda:0'
    )
    #currModel = YOLO(model_path)
    for i in range(0, 6):
        result = get_sliced_prediction(
            f"/Users/ashwinbardhwaj/Documents/PATH/Work Zone Project/ucb-wzdx/src/dashcam_refiner/dash_videos/Bancroft_Vid_2/Frame_Images/frame{i}.jpg",
            detection_model,
            slice_height=1024,
            slice_width=1024,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2
        )
        result.export_visuals(export_dir="runs/detect/inference")
        rename_file("runs/detect/inference", "prediction_visual.png", f"predicted_frame{i}.png")
        #results = currModel(f"/Users/ashwinbardhwaj/Documents/PATH/Work Zone Project/ucb-wzdx/src/dashcam_refiner/dash_videos/Bancroft_Vid_2/Frame_Images/frame{i}.jpg"
        #                    ,save=True, project="runs/detect", name="inference", exist_ok=True)
        #print(results)
        
def calculate_angle(box):
    if not isinstance(box, (list, tuple)) or len(box) != 4:
        return None

    x_min, y_min, x_max, y_max = box
    mid_x = (x_min + x_max) / 2
    mid_y = (y_min + y_max) / 2

    # Vector from origin (0, 0) to midpoint
    vector = np.array([mid_x, mid_y])

    # Horizontal vector
    horizontal_vector = np.array([1, 0])

    # Calculate the angle using arctan2
    angle_rad = np.arctan2(mid_y, mid_x)
    angle_deg = np.degrees(angle_rad)

    return angle_deg

def rename_file(directory, old_name, new_name):
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)
    try:
        os.rename(old_path, new_path)
        print(f"File '{old_name}' successfully renamed to '{new_name}'.")
        return True
    except Exception as e:
        print(f"Error renaming file: {e}")
        return False

def get_source_coords(filepath):
    """
    frame_num starts at 1
    """
    
    res = {}
    gpx_file = open(filepath, 'r')
    
    gpx = gpxpy.parse(gpx_file)
    for waypoint in gpx.waypoints:
        print(f'waypoint {waypoint.name} -> ({waypoint.latitude},{waypoint.longitude})')
        
    for track in gpx.tracks:
        for segment in track.segments:
            i = 1
            for point in segment.points:
                res[i] = (point.latitude, point.longitude)
                print(f'Point at {point.latitude},{point.longitude}')
                i+=1
    return res

def distance_spherical_law_cosines(lat1, lon1, lat2, lon2):
    R = 6371000

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad

    a = math.sin(lat1_rad) * math.sin(lat2_rad) + math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    c = math.acos(a)
    distance = R * c

    return distance


def compute_object_distance(delta_x, angle_1, angle_2):
    angle_3 = 180 - angle_1 - angle_2
    sin_1 = np.sin((np.pi * angle_1) / 180)
    sin_2 = np.sin((np.pi * angle_2) / 180)
    sin_3 = np.sin((np.pi * angle_3) / 180)

    dist_1 = (delta_x / sin_3) * sin_1
    dist_2 = (delta_x / sin_3) * sin_2
    
    

    
if __name__ == "__main__":
    #for i in range(1, 61):
    #    get_frame_at_timestamp("dash_videos/Bancroft_Vid_2/Bancroft_Vids_2.mp4", i)
    #target_name = "0_Cross-Street-road-closure_jpg.rf.b268533f2d69236b4bda24587fe8eba8"
    #label_path = f"/Users/ashwinbardhwaj/Documents/PATH/Work Zone Project/ucb-wzdx/src/dashcam_refiner/cone_dataset/labels/train/0_Cross-Street-road-closure_jpg.rf.b268533f2d69236b4bda24587fe8eba8.txt"
    #bounds = extract_coordinates(label_path)
    
    #img_path = f"/Users/ashwinbardhwaj/Documents/PATH/Work Zone Project/ucb-wzdx/src/dashcam_refiner/cone_dataset/images/train/0_Cross-Street-road-closure_jpg.rf.b268533f2d69236b4bda24587fe8eba8.jpg"
    
    #plot_Bounding_Box(img_path, bounds)
    #train_YOLO_model("traffic_cone.yaml")
    #run_YOLO_frame("/Users/ashwinbardhwaj/Documents/PATH/Work Zone Project/ucb-wzdx/runs/detect/train8/weights/best.pt")
    coord_readings = get_source_coords_at_frame("Bancroft_Videos2_Decoded.txt")
    
        