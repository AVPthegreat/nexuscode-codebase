<template>
  <div class="problem-list-container">
    <div class="page-content">
      <!-- Left Column: Problem List & Filters -->
      <div class="main-column">
        <!-- Top Topic Pills -->
        <div class="topic-bar">
          <div class="topic-scroll-container">
            <button :class="['topic-pill', { active: query.tag === '' }]" @click="filterByTag('')">
              All Topics
            </button>
            <button v-for="tag in tagList" :key="tag.name" :class="['topic-pill', { active: query.tag === tag.name }]"
              @click="filterByTag(tag.name)">
              {{ tag.name }}
            </button>
          </div>
        </div>

        <!-- Filter Controls -->
        <div class="filter-row">
          <div class="left-filters">
            <Select v-model="query.difficulty" @on-change="filterByDifficulty" class="filter-select"
              placeholder="Difficulty" style="width: 120px">
              <Option value="">Difficulty</Option>
              <Option value="Low" style="color: #00AF9B">Easy</Option>
              <Option value="Mid" style="color: #FFB800">Medium</Option>
              <Option value="High" style="color: #FF2D55">Hard</Option>
            </Select>

            <Select v-model="filterStatus" class="filter-select" placeholder="Status" style="width: 120px">
              <Option value="all">Status</Option>
              <Option value="solved">Solved</Option>
              <Option value="unsolved">Unsolved</Option>
            </Select>

            <Input v-model="query.keyword" @on-enter="filterByKeyword" placeholder="Search questions" icon="ios-search"
              class="search-input" />
          </div>

          <div class="right-controls">
            <ButtonGroup class="view-toggle" style="margin-right: 10px">
              <Button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'"
                icon="navicon-round"></Button>
              <Button :type="viewMode === 'card' ? 'primary' : 'default'" @click="viewMode = 'card'"
                icon="grid"></Button>
            </ButtonGroup>

            <Button type="primary" @click="pickone" class="pick-one-btn">
              <Icon type="shuffle"></Icon> Pick One
            </Button>
          </div>
        </div>

        <!-- List View -->
        <div v-if="viewMode === 'list'" class="problem-list-view">
          <Table :columns="problemTableColumns" :data="filteredProblemList" :loading="loadings.table"
            class="problem-table" disabled-hover></Table>
        </div>

        <!-- Card View -->
        <div v-else class="problem-card-view">
          <div class="card-grid">
            <div v-for="problem in filteredProblemList" :key="problem._id" class="problem-card"
              @click="toProblem(problem._id)">
              <div class="card-header">
                <h3 class="problem-title">{{ problem.title }}</h3>
                <Tag :color="getDifficultyColor(problem.difficulty)" class="difficulty-tag">
                  {{ problem.difficulty === 'Low' ? 'Easy' : problem.difficulty === 'Mid' ? 'Medium' : 'Hard' }}
                </Tag>
              </div>
              <div class="card-tags">
                <Tag v-for="tag in problem.tags.slice(0, 3)" :key="tag" class="tag-pill">{{ tag }}</Tag>
              </div>
              <div class="card-footer">
                <div class="acceptance">
                  <span class="label">Acceptance:</span>
                  <span class="value">{{ getACRate(problem.accepted_number, problem.submission_number) }}</span>
                </div>
                <Button type="primary" size="small" class="solve-btn">Solve Now</Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination-wrapper">
          <Pagination :total="total" :page-size.sync="query.limit" @on-change="pushRouter"
            @on-page-size-change="pushRouter" :current.sync="query.page" :show-sizer="true"></Pagination>
        </div>
      </div>

      <!-- Right Column: Sidebar -->
      <div class="sidebar-column">
        <!-- Daily Coding Streak Calendar -->
        <!-- This tracks your daily problem-solving activity, similar to GitHub's contribution graph -->
        <div class="sidebar-widget calendar-widget">
          <div class="widget-header">
            <div class="header-content">
              <h3>Daily Streak</h3>
              <Tooltip
                content="Track your daily coding activity. Solve at least one problem each day to maintain your streak!"
                placement="bottom">
                <Icon type="ios-information-circle-outline" size="16"
                  style="color: var(--nexus-text-secondary); cursor: help;"></Icon>
              </Tooltip>
            </div>
            <span class="streak-count">🔥 {{ currentStreak }} {{ currentStreak === 1 ? 'day' : 'days' }}</span>
          </div>
          <div class="calendar-placeholder">
            <!-- Calendar grid showing daily activity -->
            <!-- Active days (with dots) represent days when you solved problems -->
            <div class="calendar-grid">
              <div v-for="dayData in calendarDays" :key="dayData.day"
                :class="['day-cell', { 'current': dayData.isToday, 'active': dayData.hasActivity }]">
                {{ dayData.day }}
              </div>
            </div>
          </div>
        </div>

        <!-- Trending Companies -->
        <div class="sidebar-widget trending-widget">
          <div class="widget-header">
            <h3>Trending Companies</h3>
          </div>
          <div class="search-company">
            <Input placeholder="Search for a company..." icon="ios-search" />
          </div>
          <div class="company-tags">
            <Tag v-for="company in ['Google', 'Meta', 'Amazon', 'Microsoft', 'Apple', 'Uber']" :key="company"
              class="company-tag">
              {{ company }}
            </Tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import api from '@oj/api'
import utils from '@/utils/utils'
import { ProblemMixin } from '@oj/components/mixins'
import Pagination from '@oj/components/Pagination'

export default {
  name: 'ProblemList',
  mixins: [ProblemMixin],
  components: {
    Pagination
  },
  data() {
    return {
      tagList: [],
      problemTableColumns: [
        {
          title: 'Status',
          width: 80,
          align: 'center',
          render: (h, params) => {
            let status = params.row.my_status
            let icon = ''
            let color = ''
            if (status === 0) {
              icon = 'checkmark-circled'
              color = '#00AF9B' // Green
            } else if (status > 0) {
              icon = 'minus-circled'
              color = '#FFB800' // Yellow/Orange
            } else {
              return h('div', '') // No status
            }
            return h('Icon', {
              props: { type: icon, size: 18 },
              style: { color: color }
            })
          }
        },
        {
          title: 'Title',
          minWidth: 250,
          render: (h, params) => {
            return h('div', {
              style: { display: 'flex', alignItems: 'center', cursor: 'pointer' },
              on: { click: () => this.toProblem(params.row._id) }
            }, [
              h('span', {
                style: { marginRight: '10px', color: 'var(--nexus-text-secondary)' }
              }, params.row._id + '.'),
              h('span', {
                style: { fontWeight: '500', color: 'var(--nexus-text-primary)', fontSize: '14px' }
              }, params.row.title)
            ])
          }
        },
        {
          title: 'Acceptance',
          width: 120,
          render: (h, params) => {
            return h('span', {
              style: { color: 'var(--nexus-text-secondary)' }
            }, this.getACRate(params.row.accepted_number, params.row.submission_number))
          }
        },
        {
          title: 'Difficulty',
          width: 120,
          render: (h, params) => {
            let t = params.row.difficulty
            let color = '#00AF9B' // Easy
            let text = 'Easy'
            if (t === 'Mid') {
              color = '#FFB800' // Medium
              text = 'Medium'
            } else if (t === 'High') {
              color = '#FF2D55' // Hard
              text = 'Hard'
            }

            return h('span', {
              style: {
                color: color,
                fontWeight: '500'
              }
            }, text)
          }
        }
      ],
      problemList: [],
      limit: 20,
      total: 0,
      loadings: {
        table: true,
        tag: true
      },
      routeName: '',
      viewMode: 'list',
      sortBy: 'default',
      filterStatus: 'all',
      query: {
        keyword: '',
        difficulty: '',
        tag: '',
        page: 1,
        limit: 20
      },
      // Calendar data
      calendarDays: [],
      currentStreak: 0,
      submissionDates: new Set()
    }
  },
  mounted() {
    this.init()
    this.initCalendar()
  },
  methods: {
    init(simulate = false) {
      this.routeName = this.$route.name
      let query = this.$route.query
      this.query.difficulty = query.difficulty || ''
      this.query.keyword = query.keyword || ''
      this.query.tag = query.tag || ''
      this.query.page = parseInt(query.page) || 1
      if (this.query.page < 1) {
        this.query.page = 1
      }
      this.query.limit = parseInt(query.limit) || 20
      if (!simulate) {
        this.getTagList()
      }
      this.getProblemList()
    },
    pushRouter() {
      this.$router.push({
        name: 'problem-list',
        query: utils.filterEmptyValue(this.query)
      })
    },
    getProblemList() {
      let offset = (this.query.page - 1) * this.query.limit
      this.loadings.table = true
      api.getProblemList(offset, this.limit, this.query).then(res => {
        this.loadings.table = false
        this.total = res.data.data.total
        this.problemList = res.data.data.results
        // Note: addStatusColumn logic is handled in the column render now
      }, res => {
        this.loadings.table = false
      })
    },
    getTagList() {
      api.getProblemTagList().then(res => {
        this.tagList = res.data.data
        this.loadings.tag = false
      }, res => {
        this.loadings.tag = false
      })
    },
    filterByTag(tagName) {
      this.query.tag = tagName
      this.query.page = 1
      this.pushRouter()
    },
    filterByDifficulty(difficulty) {
      this.query.difficulty = difficulty
      this.query.page = 1
      this.pushRouter()
    },
    filterByKeyword() {
      this.query.page = 1
      this.pushRouter()
    },
    handleTagsVisible(value) {
      if (value) {
        this.problemTableColumns.push(
          {
            title: this.$i18n.t('m.Tags'),
            align: 'left',
            minWidth: 200,
            render: (h, params) => {
              let tags = []
              params.row.tags.forEach(tag => {
                tags.push(h('Tag', {
                  props: {
                    color: 'default'
                  },
                  style: {
                    marginRight: '4px',
                    marginBottom: '4px'
                  }
                }, tag))
              })
              return h('div', {
                style: {
                  margin: '8px 0',
                  display: 'flex',
                  flexWrap: 'wrap'
                }
              }, tags)
            }
          })
      } else {
        this.problemTableColumns.splice(this.problemTableColumns.length - 1, 1)
      }
    },
    onReset() {
      this.$router.push({ name: 'problem-list' })
    },
    pickone() {
      api.pickone().then(res => {
        this.$success('Good Luck')
        this.$router.push({ name: 'problem-details', params: { problemID: res.data.data } })
      })
    },
    toProblem(problemID) {
      this.$router.push({ name: 'problem-details', params: { problemID: problemID } })
    },
    getDifficultyColor(difficulty) {
      if (difficulty === 'Low') return 'green'
      if (difficulty === 'Mid') return 'orange'
      if (difficulty === 'High') return 'red'
      return 'default'
    },
    initCalendar() {
      // Generate calendar for the current month
      const today = new Date()
      const year = today.getFullYear()
      const month = today.getMonth()
      const daysInMonth = new Date(year, month + 1, 0).getDate()

      this.calendarDays = []
      for (let day = 1; day <= daysInMonth; day++) {
        this.calendarDays.push({
          day: day,
          date: new Date(year, month, day),
          isToday: day === today.getDate(),
          hasActivity: false
        })
      }

      // Fetch submission activity if user is authenticated
      if (this.isAuthenticated) {
        this.fetchSubmissionActivity()
      }
    },
    fetchSubmissionActivity() {
      // Fetch user's recent submissions to mark active days
      const params = {
        myself: 1,
        username: this.$store.getters.user.username
      }

      api.getSubmissionList(0, 100, params).then(res => {
        const submissions = res.data.data.results
        const today = new Date()
        const currentMonth = today.getMonth()
        const currentYear = today.getFullYear()

        // Process submissions to find unique days with accepted solutions
        const activeDates = new Set()
        submissions.forEach(sub => {
          if (sub.result === 0) { // Accepted
            const subDate = new Date(sub.create_time)
            if (subDate.getMonth() === currentMonth && subDate.getFullYear() === currentYear) {
              activeDates.add(subDate.getDate())
            }
          }
        })

        // Update calendar days with activity
        this.calendarDays.forEach(day => {
          day.hasActivity = activeDates.has(day.day)
        })

        // Calculate current streak
        this.calculateStreak(submissions)
      }).catch(err => {
        console.error('Failed to fetch submission activity:', err)
      })
    },
    calculateStreak(submissions) {
      // Sort submissions by date (newest first)
      const sortedSubs = submissions
        .filter(sub => sub.result === 0) // Only accepted
        .sort((a, b) => new Date(b.create_time) - new Date(a.create_time))

      if (sortedSubs.length === 0) {
        this.currentStreak = 0
        return
      }

      // Get unique days
      const uniqueDays = new Set()
      sortedSubs.forEach(sub => {
        const date = new Date(sub.create_time)
        const dayKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
        uniqueDays.add(dayKey)
      })

      const daysArray = Array.from(uniqueDays).map(key => {
        const parts = key.split('-')
        return new Date(parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2]))
      }).sort((a, b) => b - a)

      // Calculate streak from today backwards
      let streak = 0
      const today = new Date()
      today.setHours(0, 0, 0, 0)

      for (let i = 0; i < daysArray.length; i++) {
        const checkDate = new Date(today)
        checkDate.setDate(checkDate.getDate() - i)
        checkDate.setHours(0, 0, 0, 0)

        const hasActivityOnDay = daysArray.some(d => {
          d.setHours(0, 0, 0, 0)
          return d.getTime() === checkDate.getTime()
        })

        if (hasActivityOnDay) {
          streak++
        } else if (i > 0) {
          // Break streak if we miss a day (but allow today to be empty)
          break
        }
      }

      this.currentStreak = streak
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated']),
    filteredProblemList() {
      if (this.filterStatus === 'all') {
        return this.problemList
      }

      return this.problemList.filter(problem => {
        if (this.filterStatus === 'solved') {
          // Check if problem is solved (my_status === 0)
          return problem.my_status === 0
        } else if (this.filterStatus === 'unsolved') {
          // Check if problem is not solved (my_status !== 0 or undefined)
          return problem.my_status !== 0
        }
        return true
      })
    }
  },
  watch: {
    '$route'(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init(true)
      }
    },
    'isAuthenticated'(newVal) {
      if (newVal === true) {
        this.init()
      }
    }
  }
}
</script>

<style scoped lang="less">
.problem-list-container {
  width: 100%;
  padding: 20px 40px;
  background-color: var(--nexus-background);
  min-height: 100vh;
}

.page-content {
  display: flex;
  gap: 24px;
  width: 100%;
  margin: 0 auto;
}

.main-column {
  flex: 1;
  min-width: 0;
  /* Prevent flex overflow */
}

.sidebar-column {
  width: 320px;
  flex-shrink: 0;
  display: none;
  position: sticky;
  top: 120px;
  align-self: flex-start;
  max-height: calc(100vh - 140px);
  overflow-y: auto;

  /* Hidden on small screens */
  @media (min-width: 1100px) {
    display: block;
  }

  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--nexus-border);
    border-radius: 3px;

    &:hover {
      background: var(--nexus-text-secondary);
    }
  }
}

/* Topic Pills */
.topic-bar {
  margin-bottom: 20px;

  .topic-scroll-container {
    display: flex;
    overflow-x: auto;
    gap: 10px;
    padding-bottom: 5px;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      display: none;
    }

    .topic-pill {
      background: rgba(0, 0, 0, 0.05);
      border: none;
      border-radius: 20px;
      padding: 6px 16px;
      font-size: 13px;
      color: var(--nexus-text-secondary);
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;

      &:hover {
        background: rgba(0, 0, 0, 0.1);
        color: var(--nexus-text-primary);
      }

      &.active {
        background: var(--nexus-primary); // User's signature color
        color: #fff;
      }
    }
  }
}

/* Filter Row */
.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  .left-filters {
    display: flex;
    gap: 12px;
    align-items: center;
    flex: 1;

    .filter-select {
      width: 120px;
    }

    .search-input {
      width: 240px;
    }
  }
}

/* Sidebar Widgets */
.sidebar-widget {
  background: var(--nexus-surface);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid var(--nexus-border);

  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .header-content {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--nexus-text-primary);
      margin: 0;
    }

    .streak-count {
      font-size: 13px;
      font-weight: 600;
      color: var(--nexus-primary);
      background: rgba(var(--nexus-primary-rgb), 0.1);
      padding: 4px 10px;
      border-radius: 12px;
    }
  }
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;

  .day-cell {
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: var(--nexus-text-secondary);
    border-radius: 4px;
    cursor: pointer;

    &:hover {
      background: var(--nexus-surface-hover);
    }

    &.current {
      color: var(--nexus-primary);
      font-weight: bold;
      background: rgba(var(--nexus-primary-rgb), 0.1);
    }

    &.active {
      position: relative;

      &::after {
        content: '';
        position: absolute;
        bottom: 2px;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: var(--nexus-primary);
      }
    }
  }
}

.company-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;

  .company-tag {
    margin: 0;
    cursor: pointer;

    &:hover {
      color: var(--nexus-primary);
      border-color: var(--nexus-primary);
    }
  }
}

/* Card View */
.problem-card-view {
  margin-top: 20px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.problem-card {
  background: var(--nexus-surface);
  border: 1px solid var(--nexus-border);
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  height: 100%;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-color: var(--nexus-primary);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    gap: 12px;

    .problem-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--nexus-text-primary);
      margin: 0;
      line-height: 1.4;
      flex: 1;
    }

    .difficulty-tag {
      flex-shrink: 0;
    }
  }

  .card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 16px;
    flex: 1;

    .tag-pill {
      margin: 0;
      font-size: 12px;
    }
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--nexus-border);

    .acceptance {
      font-size: 13px;
      color: var(--nexus-text-secondary);

      .label {
        margin-right: 4px;
      }

      .value {
        font-weight: 600;
        color: var(--nexus-text-primary);
      }
    }

    .solve-btn {
      flex-shrink: 0;
    }
  }
}
</style>

<style lang="less">
/* Global Overrides */
.problem-list-view {
  .ivu-table-wrapper {
    border: none;
  }

  .ivu-table {
    background-color: transparent !important;

    &::before,
    &::after {
      display: none;
    }

    th {
      background: transparent;
      border-bottom: 1px solid var(--nexus-border);
      color: var(--nexus-text-secondary);
      font-weight: 500;
    }

    td {
      border-bottom: none;
      height: 50px;
    }

    /* Alternating Row Colors - Light Mode */
    .ivu-table-row:nth-child(odd) td {
      background-color: #ffffff;
    }

    .ivu-table-row:nth-child(even) td {
      background-color: #f9fafb;
    }

    .ivu-table-row:hover td {
      background-color: #f3f4f6 !important;
    }
  }
}

/* Dark Mode Specifics */
.dark-mode {
  .problem-list-container {
    background-color: #000000;
    /* Deep black background */
  }

  .topic-pill {
    background: #2d2d2d;
    color: #a0a0a0;

    &:hover {
      background: #3d3d3d;
      color: #fff;
    }

    &.active {
      background: var(--nexus-primary);
      color: #fff;
    }
  }

  .sidebar-widget {
    background: #1a1a1a;
    border-color: #333;
  }

  .problem-list-view .ivu-table {
    .ivu-table-row:nth-child(odd) td {
      background-color: #1a1a1a;
      /* Dark gray */
    }

    .ivu-table-row:nth-child(even) td {
      background-color: #000000;
      /* Black */
    }

    .ivu-table-row:hover td {
      background-color: #2d2d2d !important;
    }

    th {
      border-bottom-color: #333;
      color: #888;
    }
  }

  /* Card View Dark Mode */
  .problem-card {
    background: #1a1a1a;
    border-color: #333;

    &:hover {
      background: #161b22;
      border-color: var(--nexus-primary);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .card-footer {
      border-top-color: #333;
    }
  }

  /* Input/Select Dark Mode Overrides */
  .ivu-input,
  .ivu-select-selection {
    background-color: #2d2d2d;
    border-color: #444;
    color: #fff;
  }

  .ivu-select-dropdown {
    background-color: #2d2d2d;

    .ivu-select-item {
      color: #ccc;

      &:hover,
      &.ivu-select-item-selected {
        background-color: #444;
      }
    }
  }
}
</style>
