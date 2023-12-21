## Argument Parser
import argparse
import os
import subprocess
import numpy as np
# Parse all the required arguments
parser = argparse.ArgumentParser()

# Global arguments
parser.add_argument("-s", "--subject", help="Subject ID" )
parser.add_argument("-d", "--source_directory", help="Source Directory")
parser.add_argument("-rs","--reference_session")
parser.add_argument("-cs","--clinical_session")

# Parse the arguments
args = parser.parse_args()


# Identify the folders
subject = args.subject
source_dir = args.source_directory

reference_session = args.reference_session
clinical_session = args.clinical_session


# We need quotes around all file paths for the workspace file
module2_path = os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2')

if os.path.exists(os.path.join(module2_path,'MRI_RAS',subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')):
    mri_path = '"'+os.path.join(module2_path,'MRI_RAS',subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')+'"'
else:
    mri_path = '"'+os.path.join(module2_path,subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_ras.nii.gz')+'"'

spheres_labels = '"'+os.path.join(module2_path,subject+'_'+clinical_session+'_space-T01ct_desc-vox_electrodes_itk_snap_labels.txt')+'"'

if os.path.exists(os.path.join(module2_path,'MRI_RAS',subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w.nii.gz')):
  spheres_path = '"'+os.path.join(module2_path,subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_electrode_spheres.nii.gz')+'"'
else:
  spheres_path = '"'+os.path.join(module2_path,subject+'_'+reference_session+'_acq-3D_space-T00mri_T1w_ras_electrode_spheres.nii.gz')+'"'

ct_path = '"'+os.path.join(module2_path,subject+'_'+clinical_session+'_acq-3D_space-T00mri_ct_thresholded.nii.gz')+'"'

module2_quotes = '"'+module2_path+'"'

electrode_names = np.loadtxt(os.path.join(module2_path, subject+'_electrode_names.txt'), dtype=object)

html_top = f'''<?xml version="1.0" encoding="UTF-8" ?>
<!--ITK-SNAP (itksnap.org) Project File

This file can be moved/copied along with the images that it references
as long as the relative location of the images to the project file is 
the same. Do not modify the SaveLocation entry, or this will not work.
-->
<!DOCTYPE registry [
<!ELEMENT registry (entry*,folder*)>
<!ELEMENT folder (entry*,folder*)>
<!ELEMENT entry EMPTY>
<!ATTLIST folder key CDATA #REQUIRED>
<!ATTLIST entry key CDATA #REQUIRED>
<!ATTLIST entry value CDATA #REQUIRED>
]>
<registry>
  <entry key="SaveLocation" value={module2_quotes} />
  <entry key="Version" value="20190612" />
  <folder key="Annotations" >
    <entry key="Format" value="ITK-SNAP Annotation File" />
    <entry key="FormatDate" value="20150624" />
  </folder>
  <folder key="Layers" >
    <folder key="Layer[000]" >
      <entry key="AbsolutePath" value={mri_path} />
      <entry key="Role" value="MainRole" />
      <entry key="Tags" value="" />
      <folder key="IOHints" >
      </folder>
      <folder key="LayerMetaData" >
        <entry key="Alpha" value="255" />
        <entry key="CustomNickName" value="" />
        <entry key="Sticky" value="0" />
        <entry key="Tags" value="" />
        <folder key="DisplayMapping" >
          <folder key="ColorMap" >
            <entry key="Preset" value="Grayscale" />
          </folder>
          <folder key="Curve" >
            <entry key="NumberOfControlPoints" value="3" />
            <folder key="ControlPoint[0]" >
              <entry key="tValue" value="0" />
              <entry key="xValue" value="0" />
            </folder>
            <folder key="ControlPoint[1]" >
              <entry key="tValue" value="0.5" />
              <entry key="xValue" value="0.5" />
            </folder>
            <folder key="ControlPoint[2]" >
              <entry key="tValue" value="1" />
              <entry key="xValue" value="1" />
            </folder>
          </folder>
        </folder>
      </folder>
      <folder key="ProjectMetaData" >
        <entry key="GaussianBlurScale" value="1" />
        <entry key="RemappingExponent" value="3" />
        <entry key="RemappingSteepness" value="0.04" />
        <folder key="Files" >
          <folder key="Grey" >
            <entry key="Dimensions" value="192 256 160" />
            <entry key="Orientation" value="LPI" />
          </folder>
        </folder>
        <folder key="IOHistory" >
          <folder key="AnatomicImage" >
            <entry key="ArraySize" value="1" />
            <entry key="Element[0]" value={ct_path} />
          </folder>
          <folder key="LabelDescriptions" >
            <entry key="ArraySize" value="1" />
            <entry key="Element[0]" value={spheres_labels} />
          </folder>
          <folder key="LabelImage" >
            <entry key="ArraySize" value="1" />
            <entry key="Element[0]" value={spheres_path} />
          </folder>
        </folder>
        <folder key="IRIS" >
          <entry key="SliceViewLayerLayout" value="Stacked" />
          <folder key="BoundingBox" >
            <entry key="InterpolationMethod" value="Nearest" />
            <entry key="ResampleDimensions" value="192 256 160" />
            <entry key="SeedWithCurrentSegmentation" value="0" />
            <folder key="ROIBox[0]" >
              <entry key="Index" value="0" />
              <entry key="Size" value="192" />
            </folder>
            <folder key="ROIBox[1]" >
              <entry key="Index" value="0" />
              <entry key="Size" value="256" />
            </folder>
            <folder key="ROIBox[2]" >
              <entry key="Index" value="0" />
              <entry key="Size" value="160" />
            </folder>
          </folder>
          <folder key="DisplayMapping" >
            <folder key="ColorMap" >
              <entry key="Preset" value="Grayscale" />
            </folder>
            <folder key="Curve" >
              <entry key="NumberOfControlPoints" value="3" />
              <folder key="ControlPoint[0]" >
                <entry key="tValue" value="0" />
                <entry key="xValue" value="0" />
              </folder>
              <folder key="ControlPoint[1]" >
                <entry key="tValue" value="0.5" />
                <entry key="xValue" value="0.5" />
              </folder>
              <folder key="ControlPoint[2]" >
                <entry key="tValue" value="1" />
                <entry key="xValue" value="1" />
              </folder>
            </folder>
          </folder>
          <folder key="LabelState" >
            <entry key="CoverageMode" value="OverAll" />
            <entry key="DrawingLabel" value="1" />
            <entry key="OverwriteLabel" value="0" />
            <entry key="PolygonInvert" value="0" />
            <entry key="SegmentationAlpha" value="0.5" />
          </folder>'''

html_middle=f'''<folder key="LabelTable" >
            <entry key="NumberOfElements" value="{len(electrode_names)}" />
            '''


for i,label_name in enumerate(electrode_names):
  html_middle_template=f'''<folder key="Element[{i}]" >
                <entry key="Alpha" value="255" />
                <entry key="Color" value="0 255 0" />
                <entry key="Flags" value="1 1" />
                <entry key="Index" value="{i+1}" />
                <entry key="Label" value="{label_name}" />
              </folder>'''
  html_middle = html_middle+html_middle_template

html_bottom=f'''
</folder>
          <folder key="MeshOptions" >
            <entry key="DecimateFeatureAngle" value="45" />
            <entry key="DecimateMaximumError" value="0.002" />
            <entry key="DecimatePreserveTopology" value="1" />
            <entry key="DecimateTargetReduction" value="0.95" />
            <entry key="GaussianError" value="0.03" />
            <entry key="GaussianStandardDeviation" value="0.8" />
            <entry key="MeshSmoothingBoundarySmoothing" value="0" />
            <entry key="MeshSmoothingConvergence" value="0" />
            <entry key="MeshSmoothingFeatureAngle" value="45" />
            <entry key="MeshSmoothingFeatureEdgeSmoothing" value="0" />
            <entry key="MeshSmoothingIterations" value="20" />
            <entry key="MeshSmoothingRelaxationFactor" value="0.01" />
            <entry key="UseDecimation" value="0" />
            <entry key="UseGaussianSmoothing" value="1" />
            <entry key="UseMeshSmoothing" value="0" />
          </folder>
        </folder>
        <folder key="SNAP" >
          <folder key="SnakeParameters" >
            <entry key="AdvectionSpeedExponent" value="0" />
            <entry key="AdvectionWeight" value="0" />
            <entry key="AutomaticTimeStep" value="1" />
            <entry key="Clamp" value="1" />
            <entry key="CurvatureSpeedExponent" value="-1" />
            <entry key="CurvatureWeight" value="0.2" />
            <entry key="Ground" value="5" />
            <entry key="LaplacianSpeedExponent" value="0" />
            <entry key="LaplacianWeight" value="0" />
            <entry key="PropagationSpeedExponent" value="1" />
            <entry key="PropagationWeight" value="1" />
            <entry key="SnakeType" value="RegionCompetition" />
            <entry key="SolverAlgorithm" value="ParallelSparseField" />
            <entry key="TimeStepFactor" value="1" />
          </folder>
        </folder>
      </folder>
    </folder>
    <folder key="Layer[001]" >
      <entry key="AbsolutePath" value={ct_path} />
      <entry key="Role" value="OverlayRole" />
      <entry key="Tags" value="" />
      <folder key="IOHints" >
      </folder>
      <folder key="ImageTransform" >
        <entry key="IsIdentity" value="1" />
      </folder>
      <folder key="LayerMetaData" >
        <entry key="Alpha" value="0.5" />
        <entry key="CustomNickName" value="" />
        <entry key="Sticky" value="1" />
        <entry key="Tags" value="" />
        <folder key="DisplayMapping" >
          <folder key="ColorMap" >
            <entry key="Preset" value="Grayscale" />
          </folder>
          <folder key="Curve" >
            <entry key="NumberOfControlPoints" value="3" />
            <folder key="ControlPoint[0]" >
              <entry key="tValue" value="0" />
              <entry key="xValue" value="0" />
            </folder>
            <folder key="ControlPoint[1]" >
              <entry key="tValue" value="0.3125" />
              <entry key="xValue" value="0.5" />
            </folder>
            <folder key="ControlPoint[2]" >
              <entry key="tValue" value="0.625" />
              <entry key="xValue" value="1" />
            </folder>
          </folder>
        </folder>
      </folder>
    </folder>
    <folder key="Layer[002]" >
      <entry key="AbsolutePath" value={spheres_path} />
      <entry key="Role" value="SegmentationRole" />
      <entry key="Tags" value="" />
      <folder key="IOHints" >
      </folder>
      <folder key="LayerMetaData" >
        <entry key="Alpha" value="0" />
        <entry key="CustomNickName" value="" />
        <entry key="Sticky" value="1" />
        <entry key="Tags" value="" />
      </folder>
    </folder>
  </folder>
</registry>
'''

html_all = html_top+html_middle+html_bottom

with open(os.path.join(os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2'), subject+'_'+reference_session+'_itksnap_workspace.itksnap'), 'w') as f:
    f.write(html_all)
