def explode_commas(df, column, symbol=","):
    df = df.dropna(subset=[column])
    strings = []
    for string in df[column]:
        
        if symbol in string:
            array = string.split(symbol + " ")
            strings.append(array)
        else:
            strings.append(string)

    df[column] = strings
    print(df)
    return(df.explode(column))