import streamlit as st
from pint import PintError
import numpy as np
from convertor.convert import irr2flux, flux2irr  # Adjust import according to your package structure

st.title("Let there be Light!")


def explanation():
    ele = st.sidebar
    ele.markdown("""
    ### Definitions
    - **irradiance (I)**: The power per unit area received by a surface. Typically measured in Watts per square meter (W/m²).
    - **Photon Flux (E)**: The number of photons hitting a surface per unit area per time. Typically measured in moles of photons per square meter per second (mol/m²/s).

    ### Conversion Equations
    The conversion from photon flux to irradiance is given by:
    """)

    ele.latex(r"""
    I = \frac{E \cdot h \cdot c \cdot N_A}{\lambda}
    """)

    ele.markdown("""
    The conversion from irradiance to photon flux is given by:
    """)

    ele.latex(r"""
    E = \frac{I \cdot \lambda}{h \cdot c \cdot N_A}
    """)

    ele.markdown("""
    where:
    - $I$ is the irradiance,
    - $E$ is the photon flux,
    - $\lambda$ is the wavelength,
    - $h$ is the Planck constant,
    - $c$ is the speed of light,
    - $N_A$ is the Avogadro's number.
    """)


conversion_type = st.radio(
    "Select Conversion Type",
    ('irradiance to photonflux', 'photonflux to irradiance')
)

irr_units_list = [
    "W/m^2",
    "uW/m^2",
    "mW/m^2",
    "nW/m^2",
    "W/cm^2",
    "uW/cm^2",
    "mW/cm^2",
    "nW/cm^2",
]

flux_units_list = [
    "E",
    "uE",
    "mE",
    "nE",
]

col1, col2 = st.columns((4, 1))

if conversion_type == "irradiance to photonflux":
    convert_from = "irradiance"
    convert_to = "photonflux"
else:
    convert_from = "photonflux"
    convert_to = "irradiance"

values = col1.text_input(f"Enter {convert_from} values (comma-separated):")
if convert_from == "irradiance":
    irr_units = col2.selectbox("irradiance units", irr_units_list)
else:
    flux_units = col2.selectbox("photonflux units", flux_units_list)

wavelengths = col1.text_input("Enter wavelengths (comma-separated):")
wavelengths_units = col2.selectbox("wavelength units", ["nm", "um", "mm"])

if convert_from == "irradiance":
    return_units = col1.selectbox("photonflux units", flux_units_list)
else:
    return_units = col1.selectbox("irradiance units", irr_units_list)
    return_units = f"{return_units}/nm"


# Convert input strings to numpy arrays
try:
    values_array = np.array([float(val) for val in values.split(',') if val.strip()])
    wavelengths_array = np.array([float(wave) for wave in wavelengths.split(',') if wave.strip()])
    
    if len(wavelengths_array) == 1:
        wavelengths_array = np.ones(values_array.shape) * wavelengths_array[0]

    if len(values_array) != len(wavelengths_array):
        raise ValueError

except ValueError:
    st.warning("Please enter valid numeric values of the same length.")
    explanation()
    st.stop()

# Conversion button and logic
try:
    if conversion_type == 'irradiance to photonflux':
        # Constructing the irr_units string based on user selections
        irr_units = f"{irr_units}/{wavelengths_units}"
        result = irr2flux(values_array, wavelengths_array, return_units=True, irr_units=irr_units)
    else:
        # For flux, the prefix applies to the entire unit
        flux_units = f"{flux_units}_Q/{wavelengths_units}"
        result = flux2irr(values_array, wavelengths_array, return_units=True, flux_units=flux_units)
    
    result = result.to(return_units)

    # Display results
    st.write(f"Converted {convert_to} values:")
    
    st.dataframe(
        result.magnitude, 
        use_container_width=True, 
        column_config={"value": st.column_config.NumberColumn(f"{convert_to} ({return_units})", format="%.4e")}
    )

except ValueError:
    st.warning("Please enter valid numeric values.")
    explanation()
    st.stop()
except PintError:
    st.warning("Please enter valid units.")
    explanation()
    st.stop()
    
explanation()
