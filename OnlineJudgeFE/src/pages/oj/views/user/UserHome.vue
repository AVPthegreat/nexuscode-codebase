<template>
  <div class="dashboard-container">
    <!-- Secondary Navbar -->
    <div class="secondary-navbar">
      <div class="nav-content">
        <div class="nav-item active">
          <Icon type="ios-book-outline"></Icon> Overview
        </div>
        <div class="nav-item" @click="goToSettings">
          <Icon type="ios-person-outline"></Icon> Profile
        </div>
        <div class="nav-item" @click="goToAccount">
          <Icon type="ios-gear-outline"></Icon> Account
        </div>
        <div class="nav-item" @click="goToSecurity">
          <Icon type="ios-locked-outline"></Icon> Security
        </div>
        <div class="nav-item logout" @click="handleLogout">
          <Icon type="log-out"></Icon> Logout
        </div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Left Column: Profile Sidebar -->
      <div class="col-left">
        <div class="profile-sidebar">
          <div class="avatar-section">
            <img class="avatar" :src="profile.avatar" />
            <div class="status-badge" v-if="profile.mood">
              <Icon type="happy-outline"></Icon>
            </div>
          </div>

          <div class="profile-names">
            <h1 class="fullname">{{ profile.user ? profile.user.username : '' }}</h1>
            <h2 class="username">{{ profile.user ? profile.user.username : '' }}</h2>
          </div>

          <div class="profile-bio" v-if="profile.mood">
            {{ profile.mood }}
          </div>

          <Button type="ghost" long class="edit-profile-btn" @click="goToSettings">Edit profile</Button>

          <div class="profile-meta">
            <div class="meta-item" v-if="profile.school">
              <Icon type="ios-people-outline" class="meta-icon"></Icon>
              <span>{{ profile.school }}</span>
            </div>
            <div class="meta-item">
              <Icon type="ios-location-outline" class="meta-icon"></Icon>
              <span>India</span>
            </div>
            <div class="meta-item" v-if="profile.user && profile.user.email">
              <Icon type="ios-email-outline" class="meta-icon"></Icon>
              <a :href="'mailto:' + profile.user.email">{{ profile.user.email }}</a>
            </div>
            <div class="meta-item" v-if="profile.blog">
              <Icon type="link" class="meta-icon"></Icon>
              <a :href="profile.blog" target="_blank">{{ profile.blog }}</a>
            </div>
            <div class="meta-item" v-if="profile.github">
              <Icon type="social-github" class="meta-icon"></Icon>
              <a :href="profile.github" target="_blank">{{ getGithubUsername(profile.github) }}</a>
            </div>
          </div>

          <div class="gamification-stats">
            <div class="level-info">
              <span class="level-label">Level {{ level }}</span>
              <Progress :percent="xpPercent" status="active" :stroke-width="6" hide-info class="xp-progress"></Progress>
              <span class="xp-text">{{ profile.xp }} / {{ nextLevelXp }} XP</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Main Content -->
      <div class="col-content">
        <!-- Stats Row -->
        <div class="stats-row">
          <Card :padding="16" class="stat-card">
            <div class="stat-content">
              <span class="stat-label">{{ $t('m.UserHomeSolved') }}</span>
              <span class="stat-value">{{ profile.accepted_number }}</span>
            </div>
            <Icon type="checkmark-circled" size="24" color="#19be6b" class="stat-icon"></Icon>
          </Card>
          <Card :padding="16" class="stat-card">
            <div class="stat-content">
              <span class="stat-label">{{ $t('m.UserHomeserSubmissions') }}</span>
              <span class="stat-value">{{ profile.submission_number }}</span>
            </div>
            <Icon type="ios-paper" size="24" color="#2d8cf0" class="stat-icon"></Icon>
          </Card>
          <Card :padding="16" class="stat-card">
            <div class="stat-content">
              <span class="stat-label">{{ $t('m.UserHomeScore') }}</span>
              <span class="stat-value">{{ profile.total_score }}</span>
            </div>
            <Icon type="trophy" size="24" color="#ff9900" class="stat-icon"></Icon>
          </Card>
        </div>

        <!-- Heatmap Section -->
        <div class="content-section">
          <div class="section-header">
            <span class="section-title">{{ $t('m.Submission_Activity') }}</span>
          </div>
          <div class="heatmap-wrapper">
            <SubmissionHeatmap :username="username" v-if="username"></SubmissionHeatmap>
          </div>
        </div>

        <!-- Recent Submissions Section -->
        <div class="content-section">
          <div class="section-header">
            <span class="section-title">Recent Submissions</span>
          </div>
          <div class="submissions-scroll-container" v-if="submissions.length">
            <div class="submission-card-compact" v-for="submission in submissions" :key="submission.id"
              @click="showSubmissionCode(submission)">
              <div class="sub-header">
                <h4 class="sub-title">{{ submission.problem_title || submission.problem }}</h4>
                <span class="sub-id">#{{ submission.problem }}</span>
              </div>
              <div class="sub-meta">
                <span :class="['status-text', getStatusClass(submission.result)]">{{ getStatusText(submission.result)
                }}</span>
                <span class="separator">•</span>
                <span class="sub-lang">{{ submission.language }}</span>
                <span class="separator">•</span>
                <span class="sub-time">{{ formatTime(submission.create_time) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            No submissions yet
          </div>
        </div>

        <!-- Solved Problems List -->
        <div class="content-section">
          <div class="section-header">
            <span class="section-title">{{ $t('m.List_Solved_Problems') }}</span>
            <Button type="text" size="small" icon="refresh" @click="freshProblemDisplayID"
              v-if="refreshVisible">Sync</Button>
          </div>
          <div class="problems-list" v-if="problems.length">
            <Button type="ghost" size="small" shape="circle" v-for="problemID of problems" :key="problemID"
              @click="goProblem(problemID)" class="problem-tag">
              {{ problemID }}
            </Button>
          </div>
          <div v-else class="empty-state">
            {{ $t('m.UserHomeIntro') }}
          </div>
        </div>
      </div>
    </div>

    <!-- Submission Code Modal -->
    <Modal v-model="codeModalVisible" :width="900" :class-name="'submission-modal-' + currentSubmissionStatus">
      <div slot="header">
        <h3>{{ currentSubmission.problem_title || currentSubmission.problem }}</h3>
        <Tag :color="getStatusColor(currentSubmission.result)">{{ getStatusText(currentSubmission.result) }}</Tag>
      </div>
      <div v-if="loadingSubmission" style="text-align: center; padding: 40px;">
        <Spin size="large"></Spin>
        <p style="margin-top: 10px; color: #999;">Loading submission details...</p>
      </div>
      <div v-else>
        <div class="submission-meta" v-if="currentSubmission.statistic_info">
          <div class="meta-item">
            <strong>Language:</strong> {{ currentSubmission.language }}
          </div>
          <div class="meta-item">
            <strong>Time:</strong> {{ currentSubmission.statistic_info.time_cost }}ms
          </div>
          <div class="meta-item">
            <strong>Memory:</strong> {{ formatMemory(currentSubmission.statistic_info.memory_cost) }}
          </div>
          <div class="meta-item" v-if="currentSubmission.username">
            <strong>Author:</strong> {{ currentSubmission.username }}
          </div>
        </div>
        <div class="code-container">
          <pre><code>{{ currentSubmission.code || 'Code not available' }}</code></pre>
        </div>
        <div v-if="currentSubmission.statistic_info && currentSubmission.statistic_info.err_info" class="error-info">
          <h4>Error Information:</h4>
          <pre>{{ currentSubmission.statistic_info.err_info }}</pre>
        </div>
      </div>
      <div slot="footer">
        <Button @click="codeModalVisible = false">Close</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import time from '@/utils/time'
import api from '@oj/api'
import SubmissionHeatmap from '@oj/components/SubmissionHeatmap.vue'

export default {
  components: {
    SubmissionHeatmap
  },
  data() {
    return {
      username: '',
      profile: {},
      problems: [],
      submissions: [],
      codeModalVisible: false,
      currentSubmission: {},
      loadingSubmission: false
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    ...mapActions(['changeDomTitle']),
    init() {
      this.username = this.$route.query.username || this.$store.getters.user.username
      api.getUserInfo(this.username).then(res => {
        this.changeDomTitle({ title: res.data.data.user.username })
        this.profile = res.data.data
        this.getSolvedProblems()
        this.getRecentSubmissions()
      })
    },
    getSolvedProblems() {
      let ACMProblems = this.profile.acm_problems_status.problems || {}
      let OIProblems = this.profile.oi_problems_status.problems || {}
      let ACProblems = []
      for (let problems of [ACMProblems, OIProblems]) {
        Object.keys(problems).forEach(problemID => {
          if (problems[problemID]['status'] === 0) {
            ACProblems.push(problems[problemID]['_id'])
          }
        })
      }
      ACProblems.sort()
      this.problems = ACProblems
    },
    getRecentSubmissions() {
      const params = {
        myself: 1,
        username: this.username || this.$store.getters.user.username
      }
      api.getSubmissionList(0, 50, params).then(res => {
        this.submissions = res.data.data.results
      })
    },
    goProblem(problemID) {
      this.$router.push({ name: 'problem-details', params: { problemID: problemID } })
    },
    freshProblemDisplayID() {
      api.freshDisplayID().then(res => {
        this.$success('Update successfully')
        this.init()
      })
    },
    showSubmissionCode(submission) {
      this.currentSubmission = submission
      this.codeModalVisible = true
      this.loadingSubmission = true

      api.getSubmission(submission.id).then(res => {
        this.currentSubmission = res.data.data
        this.loadingSubmission = false
      }).catch(() => {
        this.$error('Failed to load submission details')
        this.loadingSubmission = false
      })
    },
    goToSettings() {
      this.$router.push('/setting/profile')
    },
    goToAccount() {
      this.$router.push('/setting/account')
    },
    goToSecurity() {
      this.$router.push('/setting/security')
    },
    handleLogout() {
      api.logout().then(() => {
        this.$success('Logged out successfully')
        this.$router.push('/')
        location.reload()
      })
    },
    getStatusColor(status) {
      const statusColors = {
        0: '#19be6b',   // Accepted - Green
        '-1': '#ed4014', // Wrong Answer - Red
        '-2': '#ff9900', // Compile Error - Yellow
        1: '#ed4014',   // CPU Time Limit Exceeded - Red
        2: '#ed4014',   // Real Time Limit Exceeded - Red
        3: '#ed4014',   // Memory Limit Exceeded - Red
        4: '#ed4014',   // Runtime Error - Red
        5: '#ff9900',   // System Error - Yellow
        6: '#2d8cf0',   // Pending - Blue
        7: '#2d8cf0',   // Judging - Blue
        8: '#ff9900',   // Partial Accepted - Yellow
        9: '#2d8cf0'    // Submitting - Blue
      }
      return statusColors[status] || '#808695'
    },
    getStatusText(status) {
      const statusTexts = {
        '-2': 'Compile Error',
        '-1': 'Wrong Answer',
        0: 'Accepted',
        1: 'CPU Time Limit Exceeded',
        2: 'Real Time Limit Exceeded',
        3: 'Memory Limit Exceeded',
        4: 'Runtime Error',
        5: 'System Error',
        6: 'Pending',
        7: 'Judging',
        8: 'Partial Accepted',
        9: 'Submitting'
      }
      return statusTexts[status] || 'Unknown'
    },
    getStatusClass(status) {
      if (status === 0) return 'status-accepted'
      if (status === 6 || status === 7 || status === 9) return 'status-pending'
      return 'status-error'
    },
    formatTime(timestamp) {
      return time.utcToLocal(timestamp, 'YYYY-MM-DD HH:mm')
    },
    formatMemory(bytes) {
      if (!bytes) return '0KB'
      const kb = bytes / 1024
      if (kb < 1024) {
        return kb.toFixed(0) + 'KB'
      }
      return (kb / 1024).toFixed(2) + 'MB'
    },
    getGithubUsername(url) {
      if (!url) return ''
      return url.split('/').pop()
    }
  },
  computed: {
    refreshVisible() {
      if (!this.username) return true
      if (this.username && this.username === this.$store.getters.user.username) return true
      return false
    },
    level() {
      if (!this.profile.xp) return 1
      return Math.floor(Math.sqrt(this.profile.xp / 10)) + 1
    },
    nextLevelXp() {
      return 10 * Math.pow(this.level, 2)
    },
    xpPercent() {
      if (!this.profile.xp) return 0
      let currentLevelStart = 10 * Math.pow(this.level - 1, 2)
      let nextLevelStart = 10 * Math.pow(this.level, 2)
      let progress = (this.profile.xp - currentLevelStart) / (nextLevelStart - currentLevelStart) * 100
      return Math.min(Math.max(progress, 0), 100)
    },
    currentSubmissionStatus() {
      if (!this.currentSubmission.result) return 'default'
      const color = this.getStatusColor(this.currentSubmission.result)
      if (color === '#19be6b') return 'success'
      if (color === '#ed4014') return 'error'
      if (color === '#ff9900') return 'warning'
      return 'default'
    }
  },
  watch: {
    '$route'(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.init()
      }
    }
  }
}
</script>

<style lang="less" scoped>
.dashboard-container {
  width: 100%;
  min-height: 100vh;
  background: #fff;
}

// Secondary Navbar
.secondary-navbar {
  border-bottom: 1px solid #d0d7de;
  background: #f6f8fa;
  margin-bottom: 32px;
  position: sticky;
  top: 0;
  z-index: 100;

  .nav-content {
    // max-width: 1280px;
    // max-width: 100%;
    width: 100%;
    // margin: 0 auto;
    padding: 0 32px;
    display: flex;
    gap: 8px;

    .nav-item {
      padding: 16px 8px;
      font-size: 14px;
      color: #24292f;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;

      &:hover {
        background: rgba(208, 215, 222, 0.32);
      }

      &.active {
        font-weight: 600;
        border-bottom-color: #fd8c73;

        i {
          color: #57606a;
        }
      }

      &.logout {
        margin-left: auto;
        color: #cf222e;

        &:hover {
          background: #ffebe9;
        }
      }
    }
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 300px 1fr 320px;
  gap: 32px;
  // max-width: 100%;
  padding: 0 32px;
  // margin: 0 auto;
  width: 100%;
}

// Left Column: Profile Sidebar
.col-left {
  .profile-sidebar {
    position: sticky;
    top: 80px;

    .avatar-section {
      position: relative;
      margin-bottom: 16px;

      .avatar {
        width: 296px;
        height: 296px;
        border-radius: 50%;
        border: 1px solid #d0d7de;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        z-index: 1;
      }

      .status-badge {
        position: absolute;
        bottom: 30px;
        right: 30px;
        width: 38px;
        height: 38px;
        background: #fff;
        border: 1px solid #d0d7de;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        cursor: pointer;
        z-index: 2;

        &:hover {
          color: #0969da;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
      }
    }

    .profile-names {
      margin-bottom: 16px;

      .fullname {
        font-size: 24px;
        line-height: 1.25;
        font-weight: 600;
        color: #24292f;
      }

      .username {
        font-size: 20px;
        font-weight: 300;
        line-height: 24px;
        color: #57606a;
      }
    }

    .profile-bio {
      font-size: 16px;
      color: #24292f;
      margin-bottom: 16px;
    }

    .edit-profile-btn {
      width: 100%;
      margin-bottom: 16px;
      border-color: #d0d7de;
      color: #24292f;
      font-weight: 500;
      background: #f6f8fa;

      &:hover {
        background: #f3f4f6;
        border-color: #d0d7de;
      }
    }

    .profile-meta {
      margin-bottom: 24px;

      .meta-item {
        display: flex;
        align-items: center;
        margin-top: 4px;
        font-size: 14px;
        color: #24292f;

        .meta-icon {
          width: 16px;
          margin-right: 8px;
          color: #57606a;
          text-align: center;
        }

        a {
          color: #24292f;

          &:hover {
            color: #0969da;
            text-decoration: underline;
          }
        }
      }
    }

    .gamification-stats {
      padding-top: 16px;
      border-top: 1px solid #d0d7de;

      .level-info {
        .level-label {
          display: block;
          font-weight: 600;
          margin-bottom: 4px;
          color: #24292f;
        }

        .xp-text {
          display: block;
          font-size: 12px;
          color: #57606a;
          margin-top: 4px;
        }
      }
    }
  }
}

// Center Column: Main Content
.col-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 48px;

  .stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    // margin-bottom: 8px;

    .stat-card {
      border: 1px solid #d0d7de;
      border-radius: 6px;
      box-shadow: none;

      :deep(.ivu-card-body) {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
      }

      .stat-content {
        display: flex;
        flex-direction: column;

        .stat-label {
          font-size: 12px;
          color: #57606a;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: #24292f;
          line-height: 1.2;
        }
      }
    }
  }

  .content-section {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .section-title {
        font-size: 16px;
        font-weight: 400;
        color: #24292f;
      }
    }

    .heatmap-wrapper {
      border: 1px solid #d0d7de;
      border-radius: 6px;
      padding: 24px;
      background: #fff;
    }
  }

  .submissions-scroll-container {
    // display: flex;
    // overflow-x: auto;
    // gap: 16px;
    // padding-bottom: 12px;
    display: flex;
    flex-direction: column;
    max-height: 4 * 45px;
    overflow-x: auto;
    gap: 16px;


    &::-webkit-scrollbar {
      height: 8px;
    }

    &::-webkit-scrollbar-thumb {
      background: #d0d7de;
      border-radius: 4px;
    }

    .submission-card-compact {
      min-width: 300px;
      max-width: 300px;
      padding: 16px;
      border: 1px solid #d0d7de;
      border-radius: 6px;
      background: #fff;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: #0969da;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      }

      .sub-header {
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;

        .sub-title {
          font-size: 14px;
          font-weight: 600;
          color: #0969da;
          margin: 0;
          line-height: 1.4;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 220px;
        }

        .sub-id {
          font-size: 12px;
          color: #57606a;
        }
      }

      .sub-meta {
        font-size: 12px;
        color: #57606a;
        display: flex;
        align-items: center;
        flex-wrap: wrap;

        .separator {
          margin: 0 4px;
        }

        .status-text {
          font-weight: 500;

          &.status-accepted {
            color: #1a7f37;
          }

          &.status-error {
            color: #cf222e;
          }

          &.status-pending {
            color: #9a6700;
          }
        }
      }
    }
  }

  .problems-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .problem-tag {
      font-family: 'Monaco', monospace;
    }
  }

  .empty-state {
    text-align: center;
    color: #57606a;
    padding: 32px;
    border: 1px dashed #d0d7de;
    border-radius: 6px;
    font-style: italic;
  }
}

// Modal Styles
.code-container {
  max-height: 500px;
  overflow-y: auto;
  background: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
  border: 1px solid #d0d7de;

  pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;

    code {
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 12px;
      line-height: 1.5;
    }
  }
}

.submission-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  margin-bottom: 16px;

  .meta-item {
    font-size: 14px;
    color: #24292f;

    strong {
      color: #57606a;
      font-weight: 500;
      margin-right: 4px;
    }
  }
}

.error-info {
  margin-top: 16px;
  padding: 16px;
  background: #fff5f5;
  border: 1px solid #fdaeb7;
  border-radius: 6px;

  h4 {
    margin: 0 0 8px 0;
    color: #cf222e;
  }

  pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: monospace;
    font-size: 12px;
    color: #24292f;
  }
}

// Dark Mode Support
.dark-mode {
  .dashboard-container {
    background: #0d1117;
  }

  .secondary-navbar {
    background: #010409;
    border-bottom-color: #30363d;

    .nav-item {
      color: #c9d1d9;

      &:hover {
        background: rgba(177, 186, 196, 0.12);
      }

      &.active {
        border-bottom-color: #f78166;

        i {
          color: #8b949e;
        }
      }
    }
  }

  .col-left {
    .profile-sidebar {
      .avatar-section {
        .avatar {
          border-color: #30363d;
        }

        .status-badge {
          background: #0d1117;
          border-color: #30363d;
          color: #c9d1d9;
        }
      }

      .profile-names {
        .fullname {
          color: #c9d1d9;
        }

        .username {
          color: #8b949e;
        }
      }

      .profile-bio {
        color: #c9d1d9;
      }

      .edit-profile-btn {
        background: #21262d;
        border-color: #30363d;
        color: #c9d1d9;

        &:hover {
          background: #30363d;
          border-color: #8b949e;
        }
      }

      .profile-meta .meta-item {
        color: #c9d1d9;

        .meta-icon {
          color: #8b949e;
        }

        a {
          color: #c9d1d9;
        }
      }

      .gamification-stats .level-info {
        .level-label {
          color: #c9d1d9;
        }

        .xp-text {
          color: #8b949e;
        }
      }
    }
  }

  .col-content {
    .stat-card {
      background: #0d1117;
      border-color: #30363d;

      .stat-label {
        color: #8b949e;
      }

      .stat-value {
        color: #c9d1d9;
      }
    }

    .content-section {
      .section-title {
        color: #c9d1d9;
      }

      .heatmap-wrapper {
        background: #0d1117;
        border-color: #30363d;
      }
    }

    .submission-card-compact {
      background: #0d1117;
      border-color: #30363d;

      &:hover {
        border-color: #58a6ff;
      }

      .sub-title {
        color: #58a6ff;
      }

      .sub-id,
      .sub-meta {
        color: #8b949e;
      }
    }

    .empty-state {
      border-color: #30363d;
      color: #8b949e;
    }
  }

  .code-container {
    background: #0d1117;
    border-color: #30363d;

    code {
      color: #c9d1d9;
    }
  }

  .submission-meta {
    background: #0d1117;
    border-color: #30363d;

    .meta-item {
      color: #c9d1d9;

      strong {
        color: #8b949e;
      }
    }
  }
}

// Media Queries
@media (max-width: 900px) {
  .dashboard-grid {
    // grid-template-columns: 1fr;
    // padding: 0 16px;
    display: grid;
    grid-template-columns: 300px 1fr 320px;
    gap: 32px;
    padding: 0 32px;
    width: 100%;

  }

  .col-left .profile-sidebar {
    position: static;
    margin-bottom: 32px;

    .avatar-section .avatar {
      width: 100px;
      height: 100px;
    }
  }

  .secondary-navbar .nav-content {
    padding: 0 16px;
    overflow-x: auto;
  }
}
</style>
