<template>
  <div class="contribution-graph">
    <div v-if="loading" class="loading-state">
      <Spin size="large"></Spin>
      <p>Loading activity...</p>
    </div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <div v-else-if="!hasData" class="empty-state">No contributions in the last year</div>
    <div v-else class="graph-container">
      <div class="months-labels">
        <span v-for="month in monthLabels" :key="month.name + month.offset" :style="{ left: month.offset + 'px' }">
          {{ month.name }}
        </span>
      </div>
      <div class="graph-content">
        <div class="days-labels">
          <span>Mon</span>
          <span>Wed</span>
          <span>Fri</span>
        </div>
        <div class="squares-wrapper">
          <div v-for="(week, weekIndex) in weeks" :key="weekIndex" class="week-column">
            <div v-for="(day, dayIndex) in week" :key="dayIndex"
              :class="['day-square', getContributionLevel(day.count)]" @mouseenter="showTooltip(day, $event)"
              @mouseleave="hideTooltip"></div>
          </div>
        </div>
      </div>
      <div class="legend">
        <span>Less</span>
        <div class="legend-square level-0"></div>
        <div class="legend-square level-1"></div>
        <div class="legend-square level-2"></div>
        <div class="legend-square level-3"></div>
        <div class="legend-square level-4"></div>
        <span>More</span>
      </div>

      <!-- Custom Tooltip -->
      <div v-if="tooltip.visible" class="custom-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
        <strong>{{ tooltip.count }} submission{{ tooltip.count !== 1 ? 's' : '' }}</strong>
        <div class="tooltip-date">{{ tooltip.date }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import moment from 'moment'

export default {
  name: 'SubmissionHeatmap',
  props: {
    username: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      hasData: false,
      contributions: {},
      weeks: [],
      monthLabels: [],
      tooltip: {
        visible: false,
        x: 0,
        y: 0,
        count: 0,
        date: ''
      }
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.loading = true
      this.error = null

      api.getSubmissionHeatmap(this.username).then(res => {
        const data = res.data.data
        this.hasData = data && data.length > 0

        // Convert array to object for easier lookup
        this.contributions = {}
        if (data) {
          data.forEach(item => {
            this.contributions[item[0]] = item[1]
          })
        }

        this.generateCalendar()
        this.loading = false
      }).catch(err => {
        console.error('Error fetching heatmap data:', err)
        this.error = 'Failed to load activity'
        this.loading = false
      })
    },

    generateCalendar() {
      const weeks = []
      const today = moment()
      const currentYear = today.year()
      const startDate = moment(`${currentYear}-01-01`).startOf('week') // Start from first week of January
      const endDate = today

      // Calculate number of weeks from start to today
      const totalWeeks = Math.ceil(endDate.diff(startDate, 'weeks', true)) + 1

      // Generate month labels
      this.monthLabels = []
      const seenMonths = new Set()

      // Generate weeks from January to today
      for (let week = 0; week < totalWeeks; week++) {
        const weekData = []

        for (let day = 0; day < 7; day++) {
          const date = moment(startDate).add(week, 'weeks').add(day, 'days')

          if (date.isAfter(today) || date.year() !== currentYear) {
            weekData.push({ date: null, count: null })
          } else {
            const dateStr = date.format('YYYY-MM-DD')
            const count = this.contributions[dateStr] || 0
            weekData.push({ date: dateStr, count, moment: date })

            // Track month labels - only add at start of month and if we haven't seen it
            const monthKey = date.format('YYYY-MM')
            if (day === 0 && date.date() <= 7 && !seenMonths.has(monthKey)) {
              seenMonths.add(monthKey)
              this.monthLabels.push({
                name: date.format('MMM'),
                offset: week * 13
              })
            }
          }
        }

        weeks.push(weekData)
      }

      this.weeks = weeks
    },

    getContributionLevel(count) {
      if (count === null || count === 0) return 'level-0'
      if (count <= 2) return 'level-1'
      if (count <= 5) return 'level-2'
      if (count <= 10) return 'level-3'
      return 'level-4'
    },

    getTooltip(day) {
      if (!day.date) return ''
      const count = day.count || 0
      const dateStr = day.moment.format('MMM D, YYYY')
      return `${count} submission${count !== 1 ? 's' : ''} on ${dateStr}`
    },

    showTooltip(day, event) {
      if (!day.date) return

      const rect = event.target.getBoundingClientRect()
      const container = this.$el.getBoundingClientRect()

      this.tooltip.visible = true
      this.tooltip.count = day.count || 0
      this.tooltip.date = day.moment.format('MMM D, YYYY')
      this.tooltip.x = rect.left - container.left + rect.width / 2
      this.tooltip.y = rect.top - container.top - 10
    },

    hideTooltip() {
      this.tooltip.visible = false
    }
  },
  watch: {
    username() {
      this.fetchData()
    }
  }
}
</script>

<style lang="less" scoped>
.contribution-graph {
  width: 100%;
  padding: 10px 0;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 30px;
  color: #999;
}

.error-state {
  color: #ed4014;
}

.graph-container {
  position: relative;
}

.months-labels {
  position: relative;
  height: 20px;
  margin-bottom: 8px;

  span {
    position: absolute;
    font-size: 12px;
    font-weight: 500;
    color: #333;
  }
}

.graph-content {
  display: flex;
  gap: 3px;
}

.days-labels {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  padding-right: 5px;
  font-size: 10px;
  color: #666;

  span {
    height: 10px;
    line-height: 10px;
    display: block;
  }
}

.squares-wrapper {
  display: flex;
  gap: 3px;
  flex: 1;
  overflow-x: auto;

  &::-webkit-scrollbar {
    height: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 2px;
  }
}

.week-column {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.day-square {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.1s ease;

  &:hover {
    outline: 1px solid rgba(0, 0, 0, 0.3);
    outline-offset: 1px;
  }

  &.level-0 {
    background-color: #ebedf0;
  }

  &.level-1 {
    background-color: #9be9a8;
  }

  &.level-2 {
    background-color: #40c463;
  }

  &.level-3 {
    background-color: #30a14e;
  }

  &.level-4 {
    background-color: #216e39;
  }
}

.legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 3px;
  margin-top: 10px;
  font-size: 11px;
  color: #666;

  .legend-square {
    width: 10px;
    height: 10px;
    border-radius: 2px;
  }
}

// Dark mode support
.dark-mode {

  .months-labels span,
  .days-labels span,
  .legend {
    color: #aaa;
  }

  .day-square {
    &.level-0 {
      background-color: #161b22;
    }

    &:hover {
      outline-color: rgba(255, 255, 255, 0.3);
    }
  }

  .custom-tooltip {
    background: #2c2c2c;
    color: #fff;
    border-color: #444;
  }
}

.custom-tooltip {
  position: absolute;
  background: #24292e;
  color: #fff;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 1000;
  transform: translate(-50%, -100%);
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);

  &::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #24292e;
  }

  strong {
    display: block;
    margin-bottom: 2px;
  }

  .tooltip-date {
    font-size: 11px;
    opacity: 0.8;
  }
}
</style>
```
