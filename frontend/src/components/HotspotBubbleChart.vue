<template>
  <div ref="chartContainer" class="chart-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

interface Hotspot {
  id: string
  title: string
  url: string
  heat_score: number
  match_score: number
  tags?: string[]
  platform?: string  // 平台信息
}

interface CategoryData {
  category: string
  live_room_name: string
  live_room_id: string
  hotspots: Hotspot[]
}

interface Props {
  data: {
    categories: CategoryData[]
  }
}

const props = defineProps<Props>()
const emit = defineEmits<{
  bubbleClick: [hotspot: Hotspot]
}>()

const chartContainer = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 平台颜色映射（潘通色系，同色系不同透明度）
// 使用潘通经典蓝色系（Pantone Classic Blue 19-4052），不同平台用不同透明度
// 基础色：RGB(15, 76, 129) = #0F4C81
const pantoneBaseColor = { r: 15, g: 76, b: 129 }  // Pantone Classic Blue 19-4052
// 小红书品牌色：红色系 RGB(255, 51, 51) = #FF3333
const xiaohongshuColor = { r: 255, g: 51, b: 51 }  // 小红书红色
const platformColors: Record<string, string> = {
  'douyin': `rgba(${pantoneBaseColor.r}, ${pantoneBaseColor.g}, ${pantoneBaseColor.b}, 0.9)`,      // 抖音 - 90%透明度
  'zhihu': `rgba(${pantoneBaseColor.r}, ${pantoneBaseColor.g}, ${pantoneBaseColor.b}, 0.75)`,      // 知乎 - 75%透明度
  'weibo': `rgba(${pantoneBaseColor.r}, ${pantoneBaseColor.g}, ${pantoneBaseColor.b}, 0.6)`,       // 微博 - 60%透明度
  'bilibili': `rgba(${pantoneBaseColor.r}, ${pantoneBaseColor.g}, ${pantoneBaseColor.b}, 0.45)`,  // B站 - 45%透明度
  'xiaohongshu': `rgba(${xiaohongshuColor.r}, ${xiaohongshuColor.g}, ${xiaohongshuColor.b}, 0.8)`, // 小红书 - 80%透明度（红色）
  'xhs': `rgba(${xiaohongshuColor.r}, ${xiaohongshuColor.g}, ${xiaohongshuColor.b}, 0.8)`,         // 小红书别名
  'toutiao': `rgba(${pantoneBaseColor.r}, ${pantoneBaseColor.g}, ${pantoneBaseColor.b}, 0.3)`,     // 头条 - 30%透明度
  'baidu': `rgba(${pantoneBaseColor.r}, ${pantoneBaseColor.g}, ${pantoneBaseColor.b}, 0.2)`,      // 百度 - 20%透明度
  'default': `rgba(${pantoneBaseColor.r}, ${pantoneBaseColor.g}, ${pantoneBaseColor.b}, 0.5)`     // 默认 - 50%透明度
}

// 保留类目颜色（用于兼容）
const categoryColors: Record<string, string> = {
  '女装': platformColors['douyin'],
  '童装': platformColors['zhihu'],
  '家具': platformColors['weibo'],
  '家电': platformColors['bilibili'],
  '奢侈品': platformColors['baidu'],
  '美妆': platformColors['toutiao'],
  '其他': platformColors['default']
}

const initChart = () => {
  if (!chartContainer.value) return

  // 如果已经存在实例，先销毁
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }

  chartInstance = echarts.init(chartContainer.value)

  const seriesData: any[] = []
  const categories = props.data?.categories || []
  
  // 如果没有数据，显示空图表
  if (categories.length === 0) {
    chartInstance.setOption({
      title: {
        show: true,
        text: '暂无热点数据',
        left: 'center',
        top: 'middle',
        textStyle: {
          color: '#9ca3af',
          fontSize: 16
        }
      },
      xAxis: { show: false },
      yAxis: { show: false }
    })
    return
  }

  categories.forEach((categoryData) => {
    // 按平台分组热点，每个平台用不同颜色
    const hotspotsByPlatform: Record<string, typeof categoryData.hotspots> = {}
    
    categoryData.hotspots.forEach((hotspot) => {
      const platform = hotspot.platform || 'default'
      if (!hotspotsByPlatform[platform]) {
        hotspotsByPlatform[platform] = []
      }
      hotspotsByPlatform[platform].push(hotspot)
    })
    
    // 为每个平台创建一个系列
    Object.entries(hotspotsByPlatform).forEach(([platform, platformHotspots]) => {
      const color = platformColors[platform] || platformColors['default']
      
      // 过滤低匹配度热点（阈值30%）
      const MATCH_SCORE_THRESHOLD = 0.3
      const filteredHotspots = platformHotspots.filter(
        (hotspot) => (hotspot.match_score || 0) >= MATCH_SCORE_THRESHOLD
      )
      
      const data = filteredHotspots.map((hotspot) => {
        const rawMatchScore = hotspot.match_score || 0
        
        // 对匹配度进行非线性变换（平方根），拉伸低匹配度区域，提高视觉区分度
        // 原始匹配度范围：0.3-1.0，变换后范围：sqrt(0.3) ≈ 0.55 到 1.0
        // 将0.3-1.0映射到0-1，然后应用平方根变换
        const normalizedScore = rawMatchScore >= 0.3 ? (rawMatchScore - 0.3) / (1.0 - 0.3) : 0
        const transformedScore = Math.sqrt(normalizedScore)  // 平方根变换，拉伸低值区域
        
        return {
          value: [
            hotspot.heat_score || 0,
            transformedScore  // Y轴使用变换后的匹配度
          ],
          name: hotspot.title,
          id: hotspot.id,
          url: hotspot.url,
          match_score: rawMatchScore,  // 保存原始匹配度，用于tooltip显示
          category: categoryData.category,
          live_room_name: categoryData.live_room_name,
          platform: platform,
          heat_score: hotspot.heat_score || 0  // 保存原始热度值，方便在symbolSize中使用
        }
      })

      seriesData.push({
        name: `${categoryData.category} - ${platform}`,
        type: 'scatter',
        data: data,
        symbolSize: (value: number[], params: any) => {
          // 气泡大小综合考虑热度和匹配度
          // 热度权重70%，匹配度权重30%
          const heatScore = value[0] || 0
          // 使用原始匹配度（从params.data.match_score获取），而不是变换后的值
          const rawMatchScore = params.data.match_score || 0
          
          // 热度映射：0-100 -> 15-80
          const minHeatSize = 15
          const maxHeatSize = 80
          const heatSize = minHeatSize + (heatScore / 100) * (maxHeatSize - minHeatSize)
          
          // 匹配度映射：0.3-1.0 -> 10-40（更新最小匹配度阈值）
          const minMatchSize = 10
          const maxMatchSize = 40
          const minMatch = 0.3
          const maxMatch = 1.0
          const matchSize = minMatchSize + ((rawMatchScore - minMatch) / (maxMatch - minMatch)) * (maxMatchSize - minMatchSize)
          
          // 综合大小：热度70% + 匹配度30%
          const finalSize = heatSize * 0.7 + matchSize * 0.3
          
          // 限制在合理范围内
          return Math.max(15, Math.min(100, finalSize))
        },
        itemStyle: {
          color: (params: any) => {
            // 根据匹配度调整颜色透明度，匹配度越高，颜色越深
            // 使用原始匹配度（从params.data.match_score获取），而不是变换后的值
            const rawMatchScore = params.data.match_score || 0
            // 匹配度范围：0.3-1.0，映射到透明度：0.3-1.0（更新最小匹配度阈值）
            const minOpacity = 0.3
            const maxOpacity = 1.0
            const minScore = 0.3
            const maxScore = 1.0
            const opacity = minOpacity + (rawMatchScore - minScore) / (maxScore - minScore) * (maxOpacity - minOpacity)
            const clampedOpacity = Math.max(minOpacity, Math.min(maxOpacity, opacity))
            
            // 提取基础颜色的RGB值
            const baseColor = platformColors[params.data.platform || 'default'] || platformColors['default']
            const rgbMatch = baseColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/)
            if (rgbMatch) {
              const r = parseInt(rgbMatch[1])
              const g = parseInt(rgbMatch[2])
              const b = parseInt(rgbMatch[3])
              return `rgba(${r}, ${g}, ${b}, ${clampedOpacity})`
            }
            return color
          },
          opacity: 0.7,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.2)',
          shadowOffsetX: 2,
          shadowOffsetY: 2
        },
        emphasis: {
          itemStyle: {
            opacity: 1,
            borderColor: '#333',
            borderWidth: 2,
            shadowBlur: 15,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
            shadowOffsetX: 3,
            shadowOffsetY: 3
          }
        }
      })
    })
  })

  const option = {
    title: {
      show: false  // 隐藏标题，由父组件显示
    },
    tooltip: {
      trigger: 'item',
      appendToBody: true,  // 将tooltip渲染到body，确保链接可以点击
      renderMode: 'html',  // 使用HTML渲染模式
      formatter: (params: any) => {
        const data = params.data
        // 使用onclick事件，确保链接可以点击
        return `
          <div style="padding: 10px;">
            <div><strong>${data.name}</strong></div>
            <div>直播间：${data.live_room_name}</div>
            <div>类目：${data.category}</div>
            <div>平台：${data.platform || '未知'}</div>
            <div>热度：${data.value[0]}</div>
            <div>匹配度：${(data.match_score * 100).toFixed(1)}%</div>
            <div style="margin-top: 5px;">
              <a href="${data.url}" target="_blank" onclick="window.open('${data.url}', '_blank'); return false;" style="color: #409EFF; text-decoration: underline; cursor: pointer;">查看详情</a>
            </div>
          </div>
        `
      }
    },
    legend: {
      data: seriesData.map(s => s.name),
      bottom: 10,
      type: 'scroll'  // 如果图例太多，可以滚动
    },
    xAxis: {
      type: 'value',
      name: '热度',
      nameLocation: 'middle',
      nameGap: 30,
      scale: false,  // 不使用scale，让X轴从0开始，更直观地显示热度差异
      min: 0  // 从0开始
    },
    yAxis: {
      type: 'value',
      name: '匹配度',
      nameLocation: 'middle',
      nameGap: 50,
      scale: false,  // 不使用scale，因为我们已经做了非线性变换
      min: 0,
      max: 1,
      // 增加刻度数量
      splitNumber: 20,
      axisLabel: {
        formatter: (value: number) => {
          // 将变换后的值（0-1）反向映射回原始匹配度（0.3-1.0）
          // value = sqrt((raw - 0.3) / 0.7)，所以 raw = value^2 * 0.7 + 0.3
          const rawMatchScore = value * value * 0.7 + 0.3
          const percent = rawMatchScore * 100
          // 对于整数百分比，不显示小数
          if (percent % 1 === 0) {
            return percent.toFixed(0) + '%'
          }
          return percent.toFixed(1) + '%'
        },
        showMinLabel: true,
        showMaxLabel: true
      },
      // 增加网格线数量，提高视觉区分度
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed',
          opacity: 0.25,
          width: 1
        }
      }
    },
    series: seriesData
  }

  chartInstance.setOption(option)

  // 添加点击事件（点击气泡）
  chartInstance.on('click', (params: any) => {
    if (params.data && params.data.id) {
      // 触发自定义事件，传递热点信息
      const hotspot: Hotspot = {
        id: params.data.id,
        title: params.data.name,
        url: params.data.url,
        heat_score: params.data.value[0],
        match_score: params.data.value[1],
        tags: params.data.tags || [],
        platform: params.data.platform || 'douyin',
        created_at: ''
      }
      emit('bubbleClick', hotspot)
    }
  })
  
  // 监听tooltip中的链接点击（通过事件委托）
  if (chartContainer.value) {
    chartContainer.value.addEventListener('click', (e: Event) => {
      const target = e.target as HTMLElement
      if (target.tagName === 'A' && target.getAttribute('href')) {
        const url = target.getAttribute('href')
        if (url) {
          window.open(url, '_blank')
          e.preventDefault()
          e.stopPropagation()
        }
      }
    })
  }
}

watch(() => props.data, () => {
  if (chartInstance) {
    initChart()
  }
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  flex: 1;
  min-height: 400px;
}
</style>

