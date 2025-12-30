
# auth/auth.py
# auth/auth.py

from nubra_python_sdk.start_sdk import InitNubraSdk, NubraEnv


def authenticate_nubra(env):
    """
    Performs one-time interactive authentication using PROD environment
    (phone number, OTP, MPIN), then returns a Nubra SDK instance
    for the requested environment (UAT or PROD).

    Parameters:
        env: NubraEnv.UAT or NubraEnv.PROD

    Returns:
        InitNubraSdk instance for the requested environment
    """

    # Always authenticate via PROD (required for OTP + MPIN)
    InitNubraSdk(NubraEnv.PROD)

    # Initialize and return requested environment
    if env == NubraEnv.UAT:
        return InitNubraSdk(NubraEnv.UAT)
    elif env == NubraEnv.PROD:
        return InitNubraSdk(NubraEnv.PROD)
    else:
        raise ValueError("env must be NubraEnv.UAT or NubraEnv.PROD")




#USE IN MAIN FILE
# from nubra_python_sdk.start_sdk import NubraEnv
# from auth.auth import authenticate_nubra

# # For UAT
# nubra = authenticate_nubra(NubraEnv.UAT)

# # For PROD
# nubra = authenticate_nubra(NubraEnv.PROD)
