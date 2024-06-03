import streamlit as st
import pandas as pd
import pydeck as pdk

class ColumnMap:
    @staticmethod
    def drawing(dataframe):
        df = pd.DataFrame(dataframe)
        df['float'] = df['合計特殊出生率'].apply(lambda x: x ** 7)
        df = df[df['float'] != 0]
        
        view = pdk.ViewState(
            longitude=139.6917,
            latitude=35.6895,
            zoom=4,
            pitch=60,
        )
        
        # カラーマッピング関数
        def color_scale(rate):
            if  rate < 1:
                return [255, 0, 0]
            elif rate < 1.25:
                return [0,0,128]
            elif rate < 1.50:
                return [0,0,255]
            elif rate < 1.75:
                return [0,102,204]
            elif rate < 2.0:
                return [0,204,255]
            else:
                return [0,255,255]
        
        df['color'] = df['合計特殊出生率'].apply(color_scale)

        # レイヤーの設定
        layer = pdk.Layer(
            "ColumnLayer",
            data=df,
            get_position="[longitude, latitude]",
            radius=1000,
            elevation_scale=300,
            elevation_range=[0, df['float'].max()*100],
            get_elevation='float',
            get_fill_color='color',
            coverage=2.9, # ヘクサゴンの重なり具合
            auto_highlight=True,
            pickable=True,
            extruded=True,
        )

        # レイアウトの設定
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            tooltip={
                "html": "<b>{市区町村}</b><br><b>合計特殊出生率:</b> {合計特殊出生率}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
        )

        # Streamlitに表示
        st.pydeck_chart(r)

    @st.cache_data
    def load_data():
        df = pd.read_csv('./data/tfr_municipalities.csv')
        return df
    
    def main():
        st.title("市町村別の合計特殊出生率の可視化")
        
        df = ColumnMap.load_data()
        ColumnMap.drawing(df)

        st.markdown("""

            ※本グラフは合計特殊出生率の値を視覚的に強調するため、係数として7乗した値で描画しています。
            

        """)

        with st.expander("参照データ"):
            dic = {
                "人口動態統計特殊報告": '平成30年～令和４年人口動態保健所・市区町村別統計の概況',
                "年": "2020年（令和2年）",
                "※": "楢葉町、富岡町、川内村、大熊町、双葉町、浪江町、葛尾村、飯舘村、球磨村のデータなし",
                "URL": "https://www.mhlw.go.jp/toukei/saikin/hw/jinkou/other/hoken24/index.html"
            }
            df_info = pd.DataFrame(dic, index=[""]).T
            st.table(df_info)
        
            df_ =df.drop(df.columns[[1,2,4]], axis=1)
            st.dataframe(df_)#
        
        st.subheader("凡例")
        st.markdown("""
            <ul style="list-style-type:none;"></li>
            <li><span style="color: red;">■</span> < 1.00</li>
            <li><span style="color: #000080;">■</span> 1.00 - 1.24</li>
            <li><span style="color: #0000FF;">■</span> 1.25 - 1.49</li>
            <li><span style="color: #0066CC;">■</span> 1.50 - 1.74</li>
            <li><span style="color: #00CCFF;">■</span> 1.75 - 1.99</li>
            <li><span style="color: #00FFFF;">■</span> >= 2.00</li>            
            </ul>

        """, unsafe_allow_html=True)

if __name__ == '__main__':
    ColumnMap.main()
