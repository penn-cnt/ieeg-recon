## Argument Parser
import argparse
import os
import subprocess

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

html = f'''<?xml version="1.0" encoding="UTF-8" ?>
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
          </folder>
          <folder key="LabelTable" >
            <entry key="NumberOfElements" value="90" />
            <folder key="Element[0]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="24 226 20" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="1" />
              <entry key="Label" value="LAF1" />
            </folder>
            <folder key="Element[10]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="151 30 176" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="11" />
              <entry key="Label" value="LDA1" />
            </folder>
            <folder key="Element[11]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="30 9 21" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="12" />
              <entry key="Label" value="LDA2" />
            </folder>
            <folder key="Element[12]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="165 160 239" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="13" />
              <entry key="Label" value="LDA3" />
            </folder>
            <folder key="Element[13]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="2 195 87" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="14" />
              <entry key="Label" value="LDA4" />
            </folder>
            <folder key="Element[14]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="115 54 229" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="15" />
              <entry key="Label" value="LDA5" />
            </folder>
            <folder key="Element[15]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="157 173 28" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="16" />
              <entry key="Label" value="LDA6" />
            </folder>
            <folder key="Element[16]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="207 117 93" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="17" />
              <entry key="Label" value="LDH1" />
            </folder>
            <folder key="Element[17]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="182 1 218" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="18" />
              <entry key="Label" value="LDH2" />
            </folder>
            <folder key="Element[18]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="193 147 211" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="19" />
              <entry key="Label" value="LDH3" />
            </folder>
            <folder key="Element[19]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="53 241 251" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="20" />
              <entry key="Label" value="LDH4" />
            </folder>
            <folder key="Element[1]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="192 102 106" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="2" />
              <entry key="Label" value="LAF2" />
            </folder>
            <folder key="Element[20]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="25 188 141" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="21" />
              <entry key="Label" value="LDH5" />
            </folder>
            <folder key="Element[21]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="235 109 51" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="22" />
              <entry key="Label" value="LDH6" />
            </folder>
            <folder key="Element[22]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="125 130 54" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="23" />
              <entry key="Label" value="LMT1" />
            </folder>
            <folder key="Element[23]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="172 147 28" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="24" />
              <entry key="Label" value="LMT2" />
            </folder>
            <folder key="Element[24]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="131 225 196" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="25" />
              <entry key="Label" value="LMT3" />
            </folder>
            <folder key="Element[25]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="73 93 56" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="26" />
              <entry key="Label" value="LMT4" />
            </folder>
            <folder key="Element[26]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="202 248 9" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="27" />
              <entry key="Label" value="LP1" />
            </folder>
            <folder key="Element[27]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="33 118 166" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="28" />
              <entry key="Label" value="LP2" />
            </folder>
            <folder key="Element[28]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="89 225 98" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="29" />
              <entry key="Label" value="LP3" />
            </folder>
            <folder key="Element[29]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="28 11 180" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="30" />
              <entry key="Label" value="LP4" />
            </folder>
            <folder key="Element[2]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="182 93 124" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="3" />
              <entry key="Label" value="LAF3" />
            </folder>
            <folder key="Element[30]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="5 223 148" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="31" />
              <entry key="Label" value="LP5" />
            </folder>
            <folder key="Element[31]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="216 26 89" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="32" />
              <entry key="Label" value="LP6" />
            </folder>
            <folder key="Element[32]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="125 110 158" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="33" />
              <entry key="Label" value="LP7" />
            </folder>
            <folder key="Element[33]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="155 244 237" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="34" />
              <entry key="Label" value="LP8" />
            </folder>
            <folder key="Element[34]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="96 137 197" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="35" />
              <entry key="Label" value="LPF1" />
            </folder>
            <folder key="Element[35]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="205 203 193" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="36" />
              <entry key="Label" value="LPF2" />
            </folder>
            <folder key="Element[36]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="149 199 46" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="37" />
              <entry key="Label" value="LPF3" />
            </folder>
            <folder key="Element[37]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="210 131 254" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="38" />
              <entry key="Label" value="LPF4" />
            </folder>
            <folder key="Element[38]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="220 237 56" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="39" />
              <entry key="Label" value="LPF5" />
            </folder>
            <folder key="Element[39]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="247 108 140" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="40" />
              <entry key="Label" value="LPF6" />
            </folder>
            <folder key="Element[3]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="223 7 149" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="4" />
              <entry key="Label" value="LAF4" />
            </folder>
            <folder key="Element[40]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="31 46 191" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="41" />
              <entry key="Label" value="LPF7" />
            </folder>
            <folder key="Element[41]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="237 43 198" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="42" />
              <entry key="Label" value="LPF8" />
            </folder>
            <folder key="Element[42]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="2 88 84" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="43" />
              <entry key="Label" value="LPT1" />
            </folder>
            <folder key="Element[43]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="244 16 183" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="44" />
              <entry key="Label" value="LPT2" />
            </folder>
            <folder key="Element[44]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="221 124 210" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="45" />
              <entry key="Label" value="LPT3" />
            </folder>
            <folder key="Element[45]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="185 116 14" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="46" />
              <entry key="Label" value="LPT4" />
            </folder>
            <folder key="Element[46]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="35 94 69" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="47" />
              <entry key="Label" value="RAF1" />
            </folder>
            <folder key="Element[47]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="93 155 121" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="48" />
              <entry key="Label" value="RAF2" />
            </folder>
            <folder key="Element[48]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="219 6 77" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="49" />
              <entry key="Label" value="RAF3" />
            </folder>
            <folder key="Element[49]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="198 179 21" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="50" />
              <entry key="Label" value="RAF4" />
            </folder>
            <folder key="Element[4]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="74 215 237" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="5" />
              <entry key="Label" value="LAF5" />
            </folder>
            <folder key="Element[50]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="81 36 143" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="51" />
              <entry key="Label" value="RAF5" />
            </folder>
            <folder key="Element[51]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="187 135 134" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="52" />
              <entry key="Label" value="RAF6" />
            </folder>
            <folder key="Element[52]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="90 203 126" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="53" />
              <entry key="Label" value="RAT1" />
            </folder>
            <folder key="Element[53]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="240 7 144" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="54" />
              <entry key="Label" value="RAT2" />
            </folder>
            <folder key="Element[54]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="28 136 250" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="55" />
              <entry key="Label" value="RAT3" />
            </folder>
            <folder key="Element[55]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="112 116 92" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="56" />
              <entry key="Label" value="RAT4" />
            </folder>
            <folder key="Element[56]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="231 77 41" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="57" />
              <entry key="Label" value="RDA1" />
            </folder>
            <folder key="Element[57]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="9 155 181" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="58" />
              <entry key="Label" value="RDA2" />
            </folder>
            <folder key="Element[58]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="159 66 85" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="59" />
              <entry key="Label" value="RDA3" />
            </folder>
            <folder key="Element[59]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="58 238 164" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="60" />
              <entry key="Label" value="RDA4" />
            </folder>
            <folder key="Element[5]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="21 135 29" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="6" />
              <entry key="Label" value="LAF6" />
            </folder>
            <folder key="Element[60]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="241 219 61" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="61" />
              <entry key="Label" value="RDH1" />
            </folder>
            <folder key="Element[61]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="246 254 11" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="62" />
              <entry key="Label" value="RDH2" />
            </folder>
            <folder key="Element[62]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="129 100 97" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="63" />
              <entry key="Label" value="RDH3" />
            </folder>
            <folder key="Element[63]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="195 5 14" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="64" />
              <entry key="Label" value="RDH4" />
            </folder>
            <folder key="Element[64]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="105 198 41" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="65" />
              <entry key="Label" value="RDH5" />
            </folder>
            <folder key="Element[65]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="69 246 185" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="66" />
              <entry key="Label" value="RDH6" />
            </folder>
            <folder key="Element[66]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="66 205 117" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="67" />
              <entry key="Label" value="RMT1" />
            </folder>
            <folder key="Element[67]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="14 177 176" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="68" />
              <entry key="Label" value="RMT2" />
            </folder>
            <folder key="Element[68]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="150 75 62" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="69" />
              <entry key="Label" value="RMT3" />
            </folder>
            <folder key="Element[69]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="177 52 83" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="70" />
              <entry key="Label" value="RMT4" />
            </folder>
            <folder key="Element[6]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="182 171 128" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="7" />
              <entry key="Label" value="LAT1" />
            </folder>
            <folder key="Element[70]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="202 202 41" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="71" />
              <entry key="Label" value="RP1" />
            </folder>
            <folder key="Element[71]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="26 56 51" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="72" />
              <entry key="Label" value="RP2" />
            </folder>
            <folder key="Element[72]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="56 194 220" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="73" />
              <entry key="Label" value="RP3" />
            </folder>
            <folder key="Element[73]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="100 220 97" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="74" />
              <entry key="Label" value="RP4" />
            </folder>
            <folder key="Element[74]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="53 17 85" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="75" />
              <entry key="Label" value="RP5" />
            </folder>
            <folder key="Element[75]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="119 229 193" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="76" />
              <entry key="Label" value="RP6" />
            </folder>
            <folder key="Element[76]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="87 48 147" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="77" />
              <entry key="Label" value="RP7" />
            </folder>
            <folder key="Element[77]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="65 248 139" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="78" />
              <entry key="Label" value="RP8" />
            </folder>
            <folder key="Element[78]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="27 163 42" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="79" />
              <entry key="Label" value="RPF1" />
            </folder>
            <folder key="Element[79]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="68 185 132" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="80" />
              <entry key="Label" value="RPF2" />
            </folder>
            <folder key="Element[7]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="2 138 58" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="8" />
              <entry key="Label" value="LAT2" />
            </folder>
            <folder key="Element[80]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="30 157 169" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="81" />
              <entry key="Label" value="RPF3" />
            </folder>
            <folder key="Element[81]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="180 101 213" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="82" />
              <entry key="Label" value="RPF4" />
            </folder>
            <folder key="Element[82]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="131 30 192" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="83" />
              <entry key="Label" value="RPF5" />
            </folder>
            <folder key="Element[83]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="43 253 228" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="84" />
              <entry key="Label" value="RPF6" />
            </folder>
            <folder key="Element[84]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="123 47 167" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="85" />
              <entry key="Label" value="RPF7" />
            </folder>
            <folder key="Element[85]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="242 22 93" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="86" />
              <entry key="Label" value="RPF8" />
            </folder>
            <folder key="Element[86]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="114 106 239" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="87" />
              <entry key="Label" value="RPT1" />
            </folder>
            <folder key="Element[87]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="135 242 228" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="88" />
              <entry key="Label" value="RPT2" />
            </folder>
            <folder key="Element[88]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="171 50 49" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="89" />
              <entry key="Label" value="RPT3" />
            </folder>
            <folder key="Element[89]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="117 162 184" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="90" />
              <entry key="Label" value="RPT4" />
            </folder>
            <folder key="Element[8]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="248 248 60" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="9" />
              <entry key="Label" value="LAT3" />
            </folder>
            <folder key="Element[9]" >
              <entry key="Alpha" value="255" />
              <entry key="Color" value="36 93 156" />
              <entry key="Flags" value="1 1" />
              <entry key="Index" value="10" />
              <entry key="Label" value="LAT4" />
            </folder>
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

# Write the workspace file
with open(os.path.join(os.path.join(source_dir,subject,'derivatives','ieeg_recon', 'module2'), subject+'_'+reference_session+'_itksnap_workspace.itksnap'), 'w') as f:
    f.write(html)

