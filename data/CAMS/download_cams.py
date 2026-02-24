import os
import cdsapi
import glob
import zipfile
import xarray as xr
import shutil
import gc

c = cdsapi.Client(timeout=600)

years = range(2010, 2025)
times = ['00:00','03:00','06:00','09:00','12:00','15:00','18:00','21:00']
area = [-14.0, -58.0, -34.0, -39.0]  # (Sul e Sudeste do Brasil)
grid = [0.75, 0.75]


os.environ["CDSAPI_RC"] = r"c:\Users\gustavo.filho\.cdsapirc"
for year in years:
    # ---- GASES ----
    print(f'=============================================')
    print(f'Downloading CAMS gases for {year}...')
    target_gas = fr"C:\Users\gustavo.filho\Documents\Python\Masters\Data\CAMS\raw\pollutants_gases_{year}.nc"
    if os.path.exists(target_gas):
        os.remove(target_gas)

    c.retrieve(
        'cams-global-reanalysis-eac4',
        {
            'format': 'netcdf',
            'variable': [
                'ozone',
                'nitrogen_dioxide',
                'sulphur_dioxide',
                'carbon_monoxide',
            ],
            'model_level': ['60'],  # lowest model level (closest to surface)
            'date': f'{year}-01-01/{year}-12-31',
            'time': times,
            'type': 'analysis',
            'area': area,
            'grid': grid,
        },
        target_gas
    )


    # ---- PARTICULATES ---- (NOTE: AQUI NÃO TEM model_level!! Verificar se isso está certo)
    print(f'=============================================')
    print(f'Downloading CAMS particulates for {year}...')
    target_pm = fr"C:\Users\gustavo.filho\Documents\Python\Masters\Data\CAMS\raw\pollutants_pm_{year}.nc"
    if os.path.exists(target_pm):
        os.remove(target_pm)

    c.retrieve( 
        'cams-global-reanalysis-eac4',
        {
            'format': 'netcdf',
            'variable': [
                'particulate_matter_2.5um',
                'particulate_matter_10um',
            ],
            'date': f'{year}-01-01/{year}-12-31',
            'time': times,
            'type': 'analysis',
            'area': area,
            'grid': grid,
        },
        target_pm
    ) 




# ---- Meteorologia ---- 
os.environ["CDSAPI_RC"] = r"c:\Users\gustavo.filho\.cdsapirc_cds"
out_base = r"C:\Users\gustavo.filho\Documents\Python\Masters\Data\CAMS\raw\ERA5"
# ==============================
# Loop principal
# ==============================
for year in years:

    months = [f"{m:02d}" for m in range(1, 13)]

    for month in months:

        print("=============================================")
        print(f"Downloading ERA5 {year}-{month}...")

        target_nc  = os.path.join(out_base, f"meteo_era5_{year}{month}.nc")
        target_zip = os.path.join(out_base, f"meteo_era5_{year}{month}.zip")
        tmp_dir    = os.path.join(out_base, f"_tmp_{year}{month}")

        # ------------------------------
        # Limpeza prévia
        # ------------------------------
        for f in [target_nc, target_zip]:
            if os.path.exists(f):
                os.remove(f)

        if os.path.exists(tmp_dir):
            for f in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, f))
            os.rmdir(tmp_dir)

        # ------------------------------
        # Download (CDS sempre como ZIP)
        # ------------------------------
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'format': 'netcdf',
                'product_type': 'reanalysis',
                'variable': [
                    '10m_u_component_of_wind',
                    '10m_v_component_of_wind',
                    '2m_temperature',
                    '2m_dewpoint_temperature',
                    'boundary_layer_height',
                    'surface_solar_radiation_downwards',
                ],
                'year': str(year),
                'month': month,
                'day': [f"{d:02d}" for d in range(1, 32)],
                'time': times,
                'area': area,
                'grid': grid,
            },
            target_zip
        )

        # ------------------------------
        # Verificar ZIP
        # ------------------------------
        with open(target_zip, "rb") as f:
            if f.read(4) != b"PK\x03\x04":
                raise RuntimeError(f"{year}{month}: arquivo não é ZIP")

        # ------------------------------
        # Extrair NetCDFs
        # ------------------------------
        os.makedirs(tmp_dir, exist_ok=True)

        with zipfile.ZipFile(target_zip, "r") as z:
            z.extractall(tmp_dir)

        nc_files = glob.glob(os.path.join(tmp_dir, "*.nc"))

        if len(nc_files) == 0:
            raise RuntimeError(f"{year}{month}: nenhum NetCDF encontrado")

        # ------------------------------
        # Abrir + merge (CORRETO)
        # ------------------------------
        datasets = [xr.open_dataset(f) for f in nc_files]

        ds_merged = xr.merge(datasets, compat="override")

        # ------------------------------
        # Salvar NetCDF final
        # ------------------------------
        ds_merged.to_netcdf(target_nc)

        # ------------------------------
        # Fechar tudo (CRÍTICO no Windows)
        # ------------------------------
        for ds in datasets:
            ds.close()

        ds_merged.close()
        gc.collect()

        # ------------------------------
        # Limpeza final
        # ------------------------------
        for f in nc_files:
            os.remove(f)

        os.remove(target_zip)
        os.rmdir(tmp_dir)

        print(f"✔ ERA5 {year}-{month} salvo como NetCDF único")