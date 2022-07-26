import random
import streamlit as st
import SDC_DataPlatform as SDC
import altair as alt
import datetime
import pandas as pd


def GetDateList(start_date, end_date):
    date_list = []
    date_list.append(start_date.strftime('%Y-%m-%d'))
    while start_date < end_date:
        start_date += datetime.timedelta(days=1)
        date_list.append(start_date.strftime('%Y-%m-%d'))
    return date_list


def SampleData(data: list, count: int, eleNum: int):
    res = []
    if len(data) * (count * eleNum) == 0:
        return res
    if len(data) < (count * eleNum):
        width = 1;
    else:
        width = int(len(data) / (count * eleNum))
    for i in range(len(data)):
        if i % width == 0:
            res.append(data[i])

    st.write(f"Sampled {len(res)} rows from {len(data)} rows from selected date")
    return res


def ExtractLabel(dates):
    lables = []
    for date in dates:
        lable = SDC.QueryDataLabel(date)
        lables.extend(lable)
    return list(set(lables))


def GetChart(df: pd.DataFrame, eles: list, mode=0, width=1680):
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['time'], empty='none')

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(df).mark_point().encode(
        x='time:T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    ).properties(width=width)

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x='time:T',
    ).transform_filter(
        nearest
    ).properties(width=width)

    resList = []
    for ele in eles:
        rand_color = random.choice(SDC.color)

        #  The chart base
        base = alt.Chart(df).encode(
            alt.X('time:T', axis=alt.Axis(title=None))
        ).properties(width=width)

        # The basic line
        line = base.mark_line(interpolate='basis', color=rand_color).transform_filter(
            f'isValid(datum.{ele})').encode(
            alt.Y(f"{ele}:Q",
                  axis=alt.Axis(title=f"{ele}")
                  )
        ).properties(width=width)

        # Draw points on the line, and highlight based on selection
        points = line.mark_point().encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        ).properties(width=width)
        labeltext = line.mark_text(align='left', dx=7, dy=-25).encode(
            text=alt.condition(nearest, alt.value(ele), alt.value(' '))
        )
        # Draw text labels near the points, and highlight based on selection
        valuetext = line.mark_text(align='left', dx=7, dy=-5).encode(
            text=alt.condition(nearest, f'{ele}:Q', alt.value(' '))
        ).properties(width=width)

        timetext = line.mark_text(align='left', dx=7, dy=25).encode(
            text=alt.condition(nearest, 'hoursminutes(time):O', alt.value(' '))
        ).properties(width=width)

        daytext = line.mark_text(align='left', dx=7, dy=10).encode(
            text=alt.condition(nearest, 'monthdate(time):O', alt.value(' '))
        ).properties(width=width)
        resList.append(alt.layer(line, points, labeltext, valuetext, timetext, daytext))


    if mode == 0:
        res = resList[0]
        for item in resList[1:]:
            res = res + item

        return alt.layer(
            res, selectors, rules
        ).interactive()
    elif mode == 1:
        res = resList[0]
        res = alt.layer(res, selectors, rules).interactive()
        for item in resList[1:]:
            res = res & alt.layer(item, selectors, rules).interactive()
        return res


def GetChart_DualAxis(df: pd.DataFrame, eles: list):
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['time'], empty='none')

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(df).mark_point().encode(
        x='time:T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    #  The chart base
    base = alt.Chart(df).encode(
        alt.X('time:T', axis=alt.Axis(title=None))
    )

    line1 = base.mark_line(interpolate='basis', color='#5276A7').transform_filter(
        f'isValid(datum.{eles[0]})').encode(
        alt.Y(f"{eles[0]}:Q",
              axis=alt.Axis(title=f"{eles[0]}", titleColor='#5276A7')
              )
    )
    line2 = base.mark_line(interpolate='basis', color='#F18727').transform_filter(
        f'isValid(datum.{eles[1]})').encode(
        alt.Y(f"{eles[1]}:Q",
              axis=alt.Axis(title=f"{eles[1]}", titleColor='#F18727')
              )
    )

    comp = (line1 + line2).resolve_scale(
        y='independent'
    )

    # Draw points on the line1, and highlight based on selection
    points1 = line1.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    valuetext1 = line1.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, f"{eles[0]}:Q", alt.value(' '))
    )
    timetext1 = line1.mark_text(align='left', dx=5, dy=25).encode(
        text=alt.condition(nearest, 'hoursminutes(time):O', alt.value(' '))
    )
    daytext1 = line1.mark_text(align='left', dx=5, dy=10).encode(
        text=alt.condition(nearest, 'monthdate(time):O', alt.value(' '))
    )

    # Draw points on the line, and highlight based on selection
    points2 = line2.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    valuetext2 = line2.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, f"{eles[1]}:Q", alt.value(' '))
    )
    timetext2 = line2.mark_text(align='left', dx=5, dy=25).encode(
        text=alt.condition(nearest, 'hoursminutes(time):O', alt.value(' '))
    )
    daytext2 = line2.mark_text(align='left', dx=5, dy=10).encode(
        text=alt.condition(nearest, 'monthdate(time):O', alt.value(' '))
    )

    comp_points = (points1 + points2).resolve_scale(
        y='independent'
    )
    comp_valuetext = (valuetext1 + valuetext2).resolve_scale(
        y='independent'
    )
    comp_timetext = (timetext1 + timetext2).resolve_scale(
        y='independent'
    )
    comp_daytext = (daytext1 + daytext2).resolve_scale(
        y='independent'
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x='time:T',
    ).transform_filter(
        nearest
    )

    return alt.layer(comp, selectors, rules, comp_points, comp_valuetext, comp_timetext, comp_daytext)


def show():
    ChartNum = st.number_input("How many data chart to show", min_value=1, max_value=6, value=1, key="ChartNum")

    for i in range(ChartNum):
        with st.expander(f"DataChart {i + 1}"):
            fromDate = st.date_input("From", key=f"Chart{i + 1}FromDate")
            todate = st.date_input("To", key=f"Chart{i + 1}ToDate")

            dates = GetDateList(fromDate, todate)

            labels = ExtractLabel(dates)
            elements = st.multiselect(f"Chart {i + 1} elements", labels, key=f"Chart{i + 1}Elements")

            if elements:

                data = []
                for date in dates:
                    for ele in elements:
                        ex = SDC.QueryData(date, ele)
                        for j in range(len(ex)):
                            ex[j] = list(ex[j])
                            # 在时间前面加上日期
                            ex[j][1] = date + " " + ex[j][1]
                        data.extend(ex)
                sampled_data = SampleData(data, 300, len(elements))

                df = pd.DataFrame(sampled_data, columns=["id", "time", "name", "value"])
                df["time"] = df["time"].map(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S'))
                df["time"] = df["time"].dt.tz_localize('Asia/ShangHai')
                df = df.pivot(index="time", columns="name", values="value").reset_index()

                # 只选取了一种数据
                if len(elements) == 1:
                    width = st.slider(f"Chart{i+1}_Width", 400, 3200, 1650,100)
                    st.altair_chart(GetChart(df, elements, 0, width))

                # 选取了两种数据，可以使用双Y轴表示法
                elif len(elements) == 2:
                    isDualaxis = st.checkbox(f"Chart{i+1}_Dual_Y_Axis")
                    if isDualaxis:
                        st.altair_chart(GetChart_DualAxis(df, elements), use_container_width=True)
                    else:
                        width = st.slider(f"Chart{i+1}_Width", 400, 3200, 1650,100)
                        st.altair_chart(GetChart(df, elements, 1, width))

                elif len(elements) >= 3:
                    isOverlay = st.checkbox(f"Chart{i+1}_Overlay_mode")
                    width = st.slider(f"Chart{i+1}_Width",400,3200,1650,100)
                    if isOverlay:
                        st.altair_chart(GetChart(df, elements, 0, width))
                    else:
                        st.altair_chart(GetChart(df, elements, 1, width))

    if "df" in dir():
        with st.expander(f"Data Download"):
                download_csv = df.to_csv().encode("gbk")
                st.download_button("download selected data",download_csv,fromDate.strftime('%Y-%m-%d') + "to" + todate.strftime('%Y-%m-%d') + ".csv")




