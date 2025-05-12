![SplashScreen](images/Hapl-o-Mat_tag.png)


# Hapl-o-MatGUI v1.3K source code

## General information:
Hapl-o-MatGUI is a graphical user interface as optional extention for [Hapl-o-Mat](https://github.com/DKMS/Hapl-o-Mat) . Hapl-o-Mat is software for haplotype inference via an expectation-maximization algorithm. It supports processing and resolving various forms of HLA genotype data. Supported input formats are MAC and GLSC.

In order to use Hapl-o-Mat via the Hapl-o-MatGUI source code, you have to install both, [Hapl-o-Mat](https://github.com/DKMS/Hapl-o-Mat) and the [Hapl-o-MatGUI](https://github.com/DKMS/Hapl-o-Mat_GUI) , on your computer.

## The latest version:
The latest version of Hapl-o-MatGUI can be found on the Github server under <https://github.com/DKMS/Hapl-o-Mat_GUI> .
So far, we do not provide a Linux installer, therefore further packages have to be installed in addition to the source code.

## Dependencies
Hapl-o-MatGUI source code requires the following dependencies (versions are minimum versions):

 * Python 3.6.9
 * PyQt5 5.9.2
 * pyqtgraph 0.11.0
 * sip 4.19.8
 * numpy 1.19.2
 
## Hapl-o-MatGUI installation: 
Installation of Hapl-o-MatGUI source code is the same on Linux and Windows operating systems.
Clone the repository from [GitHub](https://github.com/DKMS/Hapl-o-Mat_GUI) to a suitable place on your computer.
Enter folder GUIsrc in a command line interpreter and start the program via

    python main.py
    
## Manual: 
For information on how to use Hapl-o-MatGUI follow the guide [ManualHapl-o-MatViaGUI](ManualHapl-o-MatViaGUI.pdf). 

## Citation: 
If you use Hapl-o-Mat and Hapl-oMatGUI for your research, please cite our publications

 * Schaefer C, Schmidt AH, Sauter J. Hapl-o-Mat: open-source software for HLA haplotype frequency estimation from ambiguous and heterogeneous data. BMC Bioinformatics. 2017;18(1):284. Published 2017 May 30. doi:10.1186/s12859-017-1692-y
 * Sauter J, Schaefer C, Schmidt AH. HLA Haplotype Frequency Estimation from Real-Life Data with the Hapl-o-Mat Software. Methods Mol Biol. 2018; 1802:275-284. doi: 10.1007/978-1-4939-8546-3_19. 
 * Solloch UV, Schmidt AH, Sauter J. Graphical user interface for the haplotype frequency estimation software Hapl-o-Mat. Hum Immunol. 2022; 83(2):107-112. doi: 10.1016/j.humimm.2021.11.002.

## Contributors:
If you want to participate in actively developing Hapl-o-MatGUI please join via Github.

## Author: 
Ute Solloch  

## Contact: 
Ute Solloch  
DKMS gGmbH  
Kressbach 1  
72072 Tuebingen, Germany  
solloch(at)dkms.de

## License:
Copyright (C) 2016, DKMS gGmbH

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program ("GNU_GeneralPublicLicense_v3"). If not, see <https://www.gnu.org/licenses/>.
