    # ------------------------------------------------
    # DATA CLEANING
    # ------------------------------------------------

    print("Starting cleaning process...")

    # ---- PRICE CLEANING ----
    print("Cleaning price column...")
    df["price_num"] = (
        df["price"].astype(str)
        .str.replace(r"[\$,]", "", regex=True)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    # remove missing or zero prices
    df = df[df["price_num"].notna() & (df["price_num"] > 0)]

    # remove extreme outliers (99.5th percentile)
    upper_cap = df["price_num"].quantile(0.995)
    df = df[df["price_num"] <= upper_cap]
    print(f"Applied outlier cap at: {upper_cap}")

    # ---- MISSING VALUE FIXES ----
    print("Filling key missing values...")
    df["neighbourhood_cleansed"] = df["neighbourhood_cleansed"].fillna("Unknown")

    # remove listings without valid coordinates
    df = df[df["latitude"].notna() & df["longitude"].notna()]

    # ---- DATA TYPE FIXES ----
    print("Fixing data types...")
    df["accommodates"] = pd.to_numeric(df["accommodates"], errors="coerce")
    df = df[df["accommodates"] > 0]  # remove invalid entries

    df["availability_365"] = pd.to_numeric(df["availability_365"], errors="coerce").fillna(0)

    # ---- AMENITIES PARSING ----
    print("Parsing amenities...")
    df["amenities_list"] = df["amenities"].apply(parse_amenities)
    df["amenity_count"] = df["amenities_list"].apply(len)

    # ---- STAY TYPE ----
    print("Classifying stay types...")
    df["stay_type"] = df["minimum_nights"].apply(classify_stay)

    # ---- PRICE PER PERSON ----
    print("Computing price-per-person...")
    df["price_per_person"] = df["price_num"] / df["accommodates"]

    # ---- OCCUPANCY & REVENUE ----
    print("Computing occupancy rate...")
    df["occupancy_rate"] = (365 - df["availability_365"]) / 365

    if "estimated_revenue_l365d" in df.columns:
        df["annual_revenue"] = df["estimated_revenue_l365d"]
    else:
        df["annual_revenue"] = np.nan

    # ---- DATA QUALITY CHECKS ----
    print("Running data quality checks...")

    assert df["price_num"].between(0, 10000).all(), "Invalid price > $10k detected"
    assert df["latitude"].between(33.0, 35.0).all(), "Latitude outside LA range"
    assert df["longitude"].between(-119.0, -117.0).all(), "Longitude outside LA range"
    assert df["id"].duplicated().sum() == 0, "Duplicate listing IDs found"

    print("All cleaning checks passed.")
