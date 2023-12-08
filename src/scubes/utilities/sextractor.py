from importlib import resources
from .data import sex

__data_files__ = resources.files(sex)

SEX_TOPHAT_FILTER = str(__data_files__ / 'tophat_3.0_3x3.conv') 
SEX_DEFAULT_FILTER = str(__data_files__ / 'default.conv') 
SEX_DEFAULT_STARNNW = str(__data_files__ / 'default.nnw') 

from sewpy import SEW
from os.path import join
from astropy.io import fits

from .io import print_level

def run_sex(sex_path, detection_fits, input_config, output_params, work_dir=None, output_file=None, overwrite=True, verbose=0):
    print_level('Running SExtractor for config:', 2, verbose)
    print_level(input_config, 2, verbose)

    sew = SEW(workdir='.' if work_dir is None else work_dir, config=input_config, sexpath=sex_path, params=output_params)
    sewcat = sew(detection_fits)
    
    if output_file is not None:
        sewcat['table'].write(output_file, format='fits', overwrite=overwrite)

    return sewcat

def run_default_catalog(sex_path, detection_fits, work_dir=None, output_file=None, verbose=0):
    params = [
        'NUMBER', 'X_IMAGE', 'Y_IMAGE',
        'THETA_WORLD', 'ERRTHETA_WORLD', 'ERRA_IMAGE', 'ERRB_IMAGE',
        'ERRTHETA_IMAGE', 'FLUX_AUTO', 'FLUXERR_AUTO',
        'ALPHA_J2000', 'DELTA_J2000', 'X_WORLD', 'Y_WORLD',
        'MAG_AUTO', 'MAG_BEST', 'MAGERR_AUTO',
        'MAGERR_BEST', 'FLUX_MAX', 'FWHM_IMAGE', 'FLAGS',
        'ELLIPTICITY','MU_THRESHOLD', 'THRESHOLD', 'BACKGROUND', 'THETA_IMAGE',
        'A_IMAGE', 'B_IMAGE','FLUX_RADIUS','ISOAREA_IMAGE'
    ]

    h = fits.getheader(detection_fits, ext=1)
    cgim_type = 'SEGMENTATION, APERTURES, OBJECTS'
    cgim_seg_name = join(work_dir, 'defcat_SEGM.fits')
    cgim_ape_name = join(work_dir, 'defcat_APER.fits')
    cgim_obj_name = join(work_dir, 'defcat_OBJ.fits')
    config = {
        'BACK_FILTERSIZE': 3,
        'BACK_SIZE': 256,
        'BACK_TYPE': 'AUTO',
        'BACK_VALUE': '0.0,0.0',
        'THRESH_TYPE': 'RELATIVE',
        'ANALYSIS_THRESH': 1.5,
        'DETECT_THRESH': 1.5,
        'DETECT_MINAREA': 5,
        'FILTER_THRESH': '',
        'FILTER': 'Y',
        'FILTER_NAME': SEX_DEFAULT_FILTER,
        'CLEAN': 'Y',
        'CLEAN_PARAM': 1.0,
        'DEBLEND_NTHRESH': 32,
        'DEBLEND_MINCONT': 0.005,
        'MASK_TYPE': 'CORRECT',
        'WEIGHT_TYPE': 'BACKGROUND',
        'WEIGHT_IMAGE': join(work_dir, 'defcat_weight.fits'),
        'WEIGHT_THRESH': '',
        'WEIGHT_GAIN': 'Y',
        'GAIN': h.get('GAIN'),
        'GAIN_KEY': 'GAIN',
        'FLAG_IMAGE': 'flag.fits',
        'FLAG_TYPE': 'OR',
        'BACKPHOTO_TYPE': 'LOCAL',
        'BACKPHOTO_THICK': 24,
        'BACK_FILTTHRESH': 0.0,
        'PHOT_AUTOPARAMS': (2.5, 3.5),
        'PHOT_AUTOAPERS': (0.0, 0.0),
        'PHOT_PETROPARAMS': (2.0, 3.5),
        'PHOT_APERTURES': (2, 28, 160),
        'PHOT_FLUXFRAC': 0.5,
        'SATUR_LEVEL': h.get('SATURATE'),
        'SATUR_KEY': 'SATURATE',
        'STARNNW_NAME': SEX_DEFAULT_STARNNW,
        'SEEING_FWHM': 1.1,
        'CATALOG_NAME': join(work_dir, 'defcat.cat'),
        'PARAMETERS_NAME': cgim_type,
        'CHECKIMAGE_TYPE': 'SEGMENTATION, APERTURES, OBJECTS',
        'CHECKIMAGE_NAME': f'{cgim_seg_name}, {cgim_ape_name}, {cgim_obj_name}',
        'INTERP_TYPE': 'NONE',
        'INTERP_MAXYLAG': 4,
        'INTERP_MAXXLAG': 4,
        'DETECT_TYPE': 'CCD',
        'MEMORY_BUFSIZE': 11000,
        'MEMORY_PIXSTACK': 3000000,
        'MEMORY_OBJSTACK': 10000,
        'PIXEL_SCALE': 0.55,
        'MAG_GAMMA': 4.0,
        'MAG_ZEROPOINT': 25.0,
        'CATALOG_TYPE': 'FITS_LDAC',
        'VERBOSE_TYPE': 'NORMAL',
        'WRITE_XML': 'Y',
        'XML_NAME': join(work_dir, 'defcat_sexout.xml'),
        'NTHREADS': 2,
    }

    sew = SEW(workdir='.' if work_dir is None else work_dir, config=config, sexpath=sex_path, params=params)
    sewcat = sew(detection_fits)
    
    if output_file is not None:
        sewcat['table'].write(output_file, format='fits', overwrite=True)

    return sewcat