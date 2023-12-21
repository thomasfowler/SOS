Science of Sales
================

# Build and Deploy

## Build

Run the following command to build using Cloud Build:

```bash
gcloud builds submit --config cloudmigrate.yaml --project science-of-sales
```
## Deploy

Run the following command to deploy to Cloud Run:

```bash
gcloud run deploy epic-sos-prod \
    --platform managed \
    --region europe-west1 \
    --image gcr.io/science-of-sales/epic-sos-prod \
    --add-cloudsql-instances science-of-sales:europe-west1:sos \
    --allow-unauthenticated
```

Note: These are configured for the Epic SoS instance. Change as needed for AdReach

For example:

### Env Vars

When deploying, you must make sure you set the following Env Vars:

GOOGLE_CLOUD_PROJECT: This ensures we get into the block of code that pulls the .env file from secret manager
SETTINGS_NAME: The name of the secret with the .env file

Otherwise, you can simply create a .env file and load that into secret manager with all the required env vars as per the
settings.py file.

```bash
gcloud builds submit --config cloudmigrate.yaml \
    --substitutions _INSTANCE_NAME=sos,_REGION=europe-west1, _SERVICE_NAME=adreach-sos-prod, _SECRET_SETTINGS_NAME=adreach_sos_settings
```

This will build with substitutions for AdReach instance.

### CORS on Cloud Storage

This only needs to be done once per bucket. It is done via the console. Here is the command for the epic config file:
```bash
gcloud storage buckets update gs://epic_sos_prod_static --cors-file=epic_storage_cors.json
```

## Data Import

### Syncing Groups

In order to sync the groups, you need to run the following command:

```bash
python manage.py sync_roles
```

This syncs groups defined in the roles.py file to the DB. This *MUST* be completed as an initial step, before importing
users.

### Import Commands

There are a number of commands, one per mode, that can be run to import data into the database. They must be run in the
order provided below:

1. Users: `python manage.py import_users data_prep/source_data/epic/users.csv`
2. Organisation Business Units: `python manage.py import_org_business_units data_prep/source_data/epic/org_bus_units.csv`
3. Media Groups: `python manage.py import_media_groups data_prep/source_data/epic/media_groups.csv`
4. Products: `python manage.py import_products data_prep/source_data/epic/products.csv`
5. Agencies: `python manage.py import_agencies data_prep/source_data/epic/agencies.csv`
6. Brands: `python manage.py import_brands data_prep/source_data/epic/brands.csv`
7. Brand Business Units: `python manage.py import_brand_business_units data_prep/source_data/epic/brand_bus.csv`
8. Opportunities: `python  manage.py import_opportunities data_prep/source_data/epic/opportunities.csv`
9. Performance History: `python manage.py import_performance_history data_prep/source_data/epic/performance_history.csv`

Obviously adjust the paths for the CSV source files you are importing.

# TODO:

1. In order to see what opportunities need to be captured for a brand, we need to provide a
    screen that shows all the current brands that do not yet have an opportunity logged for
    the current fiscal. It must obviously be filtered for the current user. In this way, a user
    can quickly see what brands they still need to plan for this year
2. Related to the item above, we should also show the user what the historic performance was
    for that *brand*... That is to say, rolled up for the brands
3. Performance history needs to link, I think, to the brand, not the opportunity...? Maybe?
4. Add / edit opportunity needs some form validation. Disable the drop downs until correct things selected etc
5. For opportunities, we probably need to track who created the opportunity, and who last updated it
6. Password reset link / workflow / page


### Notes from meeting

If not account manager, on opportunities show the rep

Add opportunity - if agency is null, then you can only choose a brand that is not associated with an agency

Create opportunity - if sales director or BU manager, you can create an opp for another user