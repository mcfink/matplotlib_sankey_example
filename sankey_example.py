for month_oi in np.arange(6, 13):
    # house sankey diagram - slide 6
    sns.set_context('talk', font_scale=1.4)

    colors = {'solar': '#DAA520',
              'coal': '#000000',
              'natural_gas': 'slateblue',
              'nuclear': 'darkgreen',
              'hydro': 'mediumblue',
              'landfill_gas': 'olive',
              'refuse': 'darkorange',
              'wind': 'lightskyblue',
              'wood': 'saddlebrown',
              'oil': 'dimgray',
              'other': 'sandybrown',
              'iso_mix': 'gray',
              'house_mix': '#AAAABB'}
    house_mix_color = '#733900'
    hatch_width = 3.0
    default_path_length = 0.5
    mpl.rcParams['hatch.linewidth'] = hatch_width
    in_home_trunk_length = 1.8
    reference_plot = False

    year_oi = 2018
    subset_df = master_df[(master_df['year'] == year_oi) & (master_df['month'] == month_oi)].copy()
    month_model_exes = list(
        subset_df[['Dry-bulb (F)', 'dayofmonth']].groupby('dayofmonth').agg(np.mean)['Dry-bulb (F)'])

    subset_df['Sum_of_all_fuels'] = subset_df[['Coal',
                                               'Natural Gas',
                                               'Nuclear',
                                               'Hydro',
                                               'Landfill Gas',
                                               'Refuse',
                                               'Solar',
                                               'Wind',
                                               'Wood',
                                               'Oil',
                                               'Other']].sum(axis=1)

    for fuel in ['Coal',
                 'Natural Gas',
                 'Nuclear',
                 'Hydro',
                 'Landfill Gas',
                 'Refuse',
                 'Solar',
                 'Wind',
                 'Wood',
                 'Oil',
                 'Other']:
        subset_df[f'{fuel}_frac'] = subset_df[fuel] / subset_df['Sum_of_all_fuels']
        subset_df[f'{fuel}_kWh_personal'] = subset_df['N01_kWh'] * subset_df[f'{fuel}_frac']

    sum_energy = subset_df[['Coal_kWh_personal',
                            'Natural Gas_kWh_personal',
                            'Nuclear_kWh_personal',
                            'Hydro_kWh_personal',
                            'Landfill Gas_kWh_personal',
                            'Refuse_kWh_personal',
                            'Solar_kWh_personal',
                            'Wind_kWh_personal',
                            'Wood_kWh_personal',
                            'Oil_kWh_personal',
                            'Other_kWh_personal',
                            'N01_kWh',
                            'NGEN_kWh',
                            'produced_Wh',
                            'solaredge_kW']].sum(axis=0)
    sum_energy['produced_kWh'] = sum_energy['produced_Wh'] / 1000.0

    fig, ax = plt.subplots(figsize=(16, 9))

    norm_factor = 1.0 * (sum_energy['N01_kWh'] + sum_energy['NGEN_kWh'])
    norm_energy = sum_energy / norm_factor
    # norm_energy['produced_kWh'] = norm_energy['solaredge_kW'] / 1000.0
    norm_energy['inverter_losses'] = norm_energy['produced_kWh'] * 0.03
    norm_energy['post_inverter_production'] = norm_energy['produced_kWh'] - norm_energy['inverter_losses']

    to_powerwall = len(subset_df[subset_df['powerwall_discharge'] == 1]['dayofmonth'].unique()) * 13.2 / norm_factor
    powerwall_losses = to_powerwall * 0.1
    powerwall_returns = to_powerwall * 0.9

    if reference_plot:
        unit = 'kWh'
        ax.text(x=-2, y=-1, s=f'Normalization factor = {norm_factor}', fontsize=10)
    else:
        unit = None
        # ax.text(x=-1, y=1, s=f'{FULL_MONTH_NAMES[month_oi-1]}', fontsize=24)
    sankey = Sankey(ax=ax, unit=unit, radius=0.15)
    # sankey 0
    sankey.add(flows=[norm_energy['produced_kWh'],
                      -norm_energy['post_inverter_production'],
                      -norm_energy['inverter_losses']],
               label='My Rooftop Solar',
               trunklength=1,
               orientations=[0, 0, 1],
               pathlengths=[0.5, 0.3, 0.5],
               facecolor=colors['solar'],
               edgecolor=colors['solar']
               )
    # sankey 1
    sankey.add(flows=[norm_energy['post_inverter_production'],
                      norm_energy[['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                   'Landfill Gas_kWh_personal',
                                   'Refuse_kWh_personal', 'Wood_kWh_personal', 'Nuclear_kWh_personal',
                                   'Wind_kWh_personal',
                                   'Hydro_kWh_personal', 'Solar_kWh_personal']].sum(),
                      -(norm_energy['N01_kWh'] + (norm_energy['post_inverter_production'] - norm_energy['NGEN_kWh'])),
                      -(norm_energy['NGEN_kWh'] - to_powerwall),
                      -to_powerwall,
                      powerwall_returns],
               label='In House Mix',
               trunklength=in_home_trunk_length,
               orientations=[0, -1, 0, -1, 1, 1],
               pathlengths=[0.5, 0.8, 0.5, 0.5, 0.5, 0.5],
               facecolor=colors['house_mix'],
               edgecolor=colors['house_mix'],
               hatch='/',
               prior=0,
               connect=(1, 0))
    # sankey 2
    sankey.add(flows=[norm_energy['Coal_kWh_personal'],
                      norm_energy['Oil_kWh_personal'],
                      norm_energy['Natural Gas_kWh_personal'],
                      norm_energy['Landfill Gas_kWh_personal'],
                      norm_energy['Refuse_kWh_personal'],
                      norm_energy['Wood_kWh_personal'],
                      norm_energy['Nuclear_kWh_personal'],
                      norm_energy['Wind_kWh_personal'],
                      norm_energy['Hydro_kWh_personal'],
                      norm_energy['Solar_kWh_personal'],
                      norm_energy['Other_kWh_personal'],
                      -norm_energy[['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                    'Landfill Gas_kWh_personal',
                                    'Refuse_kWh_personal', 'Wood_kWh_personal', 'Nuclear_kWh_personal',
                                    'Wind_kWh_personal',
                                    'Hydro_kWh_personal', 'Solar_kWh_personal']].sum()],
               label='ISO-NE Grid Mix',
               trunklength=0.3,
               orientations=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
               pathlengths=[default_path_length,
                            default_path_length + norm_energy['Coal_kWh_personal'],
                            default_path_length + norm_energy[['Oil_kWh_personal', 'Coal_kWh_personal']].sum(),
                            default_path_length + norm_energy[
                                ['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal']].sum(),
                            default_path_length + norm_energy[
                                ['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                 'Landfill Gas_kWh_personal']].sum(),
                            default_path_length + norm_energy[
                                ['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                 'Landfill Gas_kWh_personal',
                                 'Refuse_kWh_personal']].sum(),
                            default_path_length + norm_energy[
                                ['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                 'Landfill Gas_kWh_personal',
                                 'Refuse_kWh_personal', 'Wood_kWh_personal']].sum(),
                            default_path_length + norm_energy[
                                ['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                 'Landfill Gas_kWh_personal',
                                 'Refuse_kWh_personal', 'Wood_kWh_personal', 'Nuclear_kWh_personal']].sum(),
                            default_path_length + norm_energy[
                                ['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                 'Landfill Gas_kWh_personal',
                                 'Refuse_kWh_personal', 'Wood_kWh_personal', 'Nuclear_kWh_personal',
                                 'Wind_kWh_personal']].sum(),
                            default_path_length + norm_energy[
                                ['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                 'Landfill Gas_kWh_personal',
                                 'Refuse_kWh_personal', 'Wood_kWh_personal', 'Nuclear_kWh_personal',
                                 'Wind_kWh_personal',
                                 'Hydro_kWh_personal']].sum(),
                            default_path_length + norm_energy[
                                ['Oil_kWh_personal', 'Coal_kWh_personal', 'Natural Gas_kWh_personal',
                                 'Landfill Gas_kWh_personal',
                                 'Refuse_kWh_personal', 'Wood_kWh_personal', 'Nuclear_kWh_personal',
                                 'Wind_kWh_personal',
                                 'Hydro_kWh_personal', 'Solar_kWh_personal']].sum(),
                            0.3],
               facecolor=colors['iso_mix'],
               edgecolor=colors['iso_mix'],
               prior=1,
               connect=(1, 11))
    # sankey 3
    sankey.add(flows=[norm_energy['Coal_kWh_personal'],
                      -norm_energy['Coal_kWh_personal']],
               label='Coal',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['coal'],
               edgecolor=colors['coal'],
               prior=2,
               connect=(0, 1))
    # sankey 4
    sankey.add(flows=[norm_energy['Oil_kWh_personal'],
                      -norm_energy['Oil_kWh_personal']],
               label='Oil',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['oil'],
               edgecolor=colors['oil'],
               prior=2,
               connect=(1, 1))

    # sankey 5
    sankey.add(flows=[norm_energy['Natural Gas_kWh_personal'],
                      -norm_energy['Natural Gas_kWh_personal']],
               label='Natural Gas',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['natural_gas'],
               edgecolor=colors['natural_gas'],
               prior=2,
               connect=(2, 1))
    # sankey 6
    sankey.add(flows=[norm_energy['Landfill Gas_kWh_personal'],
                      -norm_energy['Landfill Gas_kWh_personal']],
               label='Landfill Gas',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['landfill_gas'],
               edgecolor=colors['landfill_gas'],
               prior=2,
               connect=(3, 1))
    # sankey 7
    sankey.add(flows=[norm_energy['Refuse_kWh_personal'],
                      -norm_energy['Refuse_kWh_personal']],
               label='Refuse',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['refuse'],
               edgecolor=colors['refuse'],
               prior=2,
               connect=(4, 1))
    # sankey 8
    sankey.add(flows=[norm_energy['Wood_kWh_personal'],
                      -norm_energy['Wood_kWh_personal']],
               label='Wood',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['wood'],
               edgecolor=colors['wood'],
               prior=2,
               connect=(5, 1))
    # sankey 9
    sankey.add(flows=[norm_energy['Nuclear_kWh_personal'],
                      -norm_energy['Nuclear_kWh_personal']],
               label='Nuclear',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['nuclear'],
               edgecolor=colors['nuclear'],
               prior=2,
               connect=(6, 1))
    # sankey 10
    sankey.add(flows=[norm_energy['Wind_kWh_personal'],
                      -norm_energy['Wind_kWh_personal']],
               label='Wind',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['wind'],
               edgecolor=colors['wind'],
               prior=2,
               connect=(7, 1))
    # sankey 11
    sankey.add(flows=[norm_energy['Hydro_kWh_personal'],
                      -norm_energy['Hydro_kWh_personal']],
               label='Hydro',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['hydro'],
               edgecolor=colors['hydro'],
               prior=2,
               connect=(8, 1))
    # sankey 12
    sankey.add(flows=[norm_energy['Solar_kWh_personal'],
                      -norm_energy['Solar_kWh_personal']],
               label='Solar',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['solar'],
               edgecolor=colors['solar'],
               prior=2,
               connect=(9, 1))
    # sankey 13
    sankey.add(flows=[norm_energy['Other_kWh_personal'],
                      -norm_energy['Other_kWh_personal']],
               label='Other',
               trunklength=0.3,
               orientations=[0, 0],
               pathlengths=[0.5, 0.5],
               facecolor=colors['other'],
               edgecolor=colors['other'],
               prior=2,
               connect=(10, 1))
    # sankey 14
    sankey.add(flows=[(norm_energy['NGEN_kWh'] - to_powerwall),
                      -(norm_energy['NGEN_kWh'] - to_powerwall)],
               label='Back to Grid',
               trunklength=0.3,
               orientations=[0, 1],
               pathlengths=[0.5, 0.5],
               facecolor=colors['solar'],
               edgecolor='green',
               hatch='//',
               prior=1,
               connect=(3, 0))
    # sankey 15 - powerwall sankey
    sankey.add(flows=[to_powerwall, -powerwall_losses, -powerwall_returns],
               label='To Powerwall',
               orientations=[1, -1, 1],
               trunklength=in_home_trunk_length,
               pathlengths=[0.5, 0.3, 0.5],
               facecolor='green',
               edgecolor='green',
               prior=1,
               connect=(4, 0))

    days_in_month = len(month_model_exes)

    total_energy = np.nansum([five_parameter_model(x, coeff_2018[0], coeff_2018[1],
                                                   coeff_2018[2], coeff_2018[3], coeff_2018[4]) for x in
                              month_model_exes])
    baseline_usage = (coeff_2018[2] + coeff_2018[3] * coeff_2018[0]) * days_in_month
    baseline_ratio = baseline_usage / total_energy
    print(total_energy, baseline_ratio, baseline_usage)

    # sankey 16 - climate control
    sankey.add(flows=[(norm_energy['N01_kWh'] + (norm_energy['post_inverter_production'] - norm_energy['NGEN_kWh'])),
                      -(1 - baseline_ratio) * (norm_energy['N01_kWh'] + (
                                  norm_energy['post_inverter_production'] - norm_energy['NGEN_kWh'])),
                      -baseline_ratio * (norm_energy['N01_kWh'] + (
                                  norm_energy['post_inverter_production'] - norm_energy['NGEN_kWh']))],
               label='In-house Usage',
               orientations=[0, 1, 0],
               pathlengths=[0.3, 0.3, 0.8],
               trunklength=0.7,
               facecolor='blue',
               edgecolor='blue',
               prior=1,
               connect=(2, 0))

    # sankey 17 - climate control out
    sankey.add(flows=[(1 - baseline_ratio) * (
                norm_energy['N01_kWh'] + (norm_energy['post_inverter_production'] - norm_energy['NGEN_kWh'])),
                      -(1 - baseline_ratio) * (norm_energy['N01_kWh'] + (
                                  norm_energy['post_inverter_production'] - norm_energy['NGEN_kWh']))],
               label='In-house Usage',
               orientations=[0, -1],
               pathlengths=[0.4, 0.7],
               trunklength=0.4,
               facecolor='blue',
               edgecolor='red',
               hatch='//',
               prior=16,
               connect=(1, 0))

    # sankey.add(flows=[-.25, 0.15, 0.1], label='two',
    #           orientations=[0, 1, -1], prior=0, connect=(0, 0))
    diagrams = sankey.finish()
    for d in diagrams:
        for t in d.texts:
            t.set_horizontalalignment('center')
            t.set_fontsize(10)
    plt.tight_layout()

    if reference_plot == True:
        plt.legend()
        filename_adder = '_ref'
    else:
        filename_adder = ''
        ax.axis('off')
    fig.savefig(f'sankey{month_oi}_{filename_adder}.png', dpi=300)