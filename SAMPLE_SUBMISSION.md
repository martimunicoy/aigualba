# Sample Submission Feature

## Overview
The Aigualba application now supports submitting water quality samples through a comprehensive web form. Users can input detailed water quality parameters, and the system validates the data before storing it in the database.

## Database Schema
The `mostres` table contains the following fields:

### Required Fields
- `data` (DATE) - Sample collection date
- `punt_mostreig` (VARCHAR) - Sampling location/point

### Optional Water Quality Parameters
- `temperatura` (DECIMAL) - Temperature in Celsius (-5 to 60°C)
- `ph` (DECIMAL) - pH level (0 to 14)
- `conductivitat_20c` (DECIMAL) - Conductivity at 20°C (μS/cm)
- `terbolesa` (DECIMAL) - Turbidity (UNF)
- `color` (DECIMAL) - Color (mg/l Pt-Co)
- `olor` (DECIMAL) - Odor index at 25°C
- `sabor` (DECIMAL) - Taste index at 25°C

### Chlorine Parameters
- `clor_lliure` (DECIMAL) - Free chlorine (mg Cl₂/l)
- `clor_total` (DECIMAL) - Total chlorine (mg Cl₂/l)

*Note: Combined chlorine (clor combinat) is calculated automatically as `clor_total - clor_lliure`*

### Microbiological Parameters
- `recompte_escherichia_coli` (DECIMAL) - E. coli count (NPM/100 ml)
- `recompte_enterococ` (DECIMAL) - Enterococcus count (NPM/100 ml)
- `recompte_microorganismes_aerobis_22c` (DECIMAL) - Aerobic microorganisms at 22°C (ufc/1 ml)
- `recompte_coliformes_totals` (DECIMAL) - Total coliforms (NMP/100 ml)

### Haloacetic Acids (Optional)
- `acid_monocloroacetic` (DECIMAL) - Monochloroacetic acid (μg/l)
- `acid_dicloroacetic` (DECIMAL) - Dichloroacetic acid (μg/l)
- `acid_tricloroacetic` (DECIMAL) - Trichloroacetic acid (μg/l)
- `acid_monobromoacetic` (DECIMAL) - Monobromoacetic acid (μg/l)
- `acid_dibromoacetic` (DECIMAL) - Dibromoacetic acid (μg/l)

## Frontend Validation

The frontend includes comprehensive validation:

### Error Validation (Prevents Submission)
1. **Required Fields**: Date and sampling point must be provided
2. **Chlorine Logic**: Free chlorine cannot exceed total chlorine
3. **Range Validation**: All parameters are validated against realistic ranges

### Warning Validation (Allows Submission with Warnings)
1. **pH Range**: Warning if pH is outside drinking water standards (6.5-9.5)
2. **Chlorine Logic**: Warning if free chlorine exceeds total chlorine
3. **Microbiological Contamination**: Warnings for presence of harmful microorganisms
4. **Temperature Range**: Warning for unusual temperature readings

## API Endpoints

### GET /api/mostres
Retrieve all sample data, ordered by date (most recent first)

### POST /api/mostres
Submit new sample data with validation

**Request Body Example:**
```json
{
  "data": "2024-11-26",
  "punt_mostreig": "Dipòsit principal",
  "temperatura": 20.5,
  "ph": 7.2,
  "clor_lliure": 0.5,
  "clor_total": 0.8,
  "recompte_escherichia_coli": 0.0
}
```

**Response:**
```json
{
  "message": "Sample created successfully",
  "id": 123
}
```

## Frontend Form Features

1. **Organized Sections**: Form is divided into logical sections (basic info, physical/chemical, chlorine, microbiological, acids)
2. **Input Validation**: Real-time validation with appropriate input types and ranges
3. **Collapsible Sections**: Advanced parameters (acids) are in a collapsible section
5. **Automatic Calculations**: Combined chlorine is calculated automatically from total and free chlorine
6. **Visual Feedback**: Color-coded validation messages (errors in red, warnings in orange)
7. **Help Text**: Contextual information and examples for each field
8. **Responsive Design**: Works on desktop and mobile devices

## Usage Instructions

1. Navigate to the Submit page (/submit)
2. Fill in the required fields (date and sampling point)
3. Add any relevant water quality measurements
4. Review validation messages if any appear
5. Submit the form
6. Confirm successful submission or address any errors

## Database Setup

To create the new table structure:

```bash
cd /Users/martimunicoy/repos/aigualba/db
python setup_database.py
```

This will create both the existing `parameters` table and the new `mostres` table with the proper schema.