<template>
  <div class="flex-container">
    <div id="contest-main">
      <!--children-->
      <transition name="fadeInUp">
        <router-view></router-view>
      </transition>
      <!--children end-->
      <div class="flex-container" v-if="route_name === 'contest-details'">
        <template>
          <div id="contest-desc">
            <Panel :padding="20" shadow>
              <div slot="title">
                {{contest.title}}
              </div>
              <div slot="extra" class="countdown-actions">
                <Tag type="dot" :color="countdownColor">
                  <span id="countdown">{{countdown}}</span>
                </Tag>
                <Button v-if="!contestStarted" class="start-btn" @click="handleStartContest">Start Contest</Button>
                <Button v-else type="error" ghost class="stop-btn" @click="handleStopContest">Stop</Button>
              </div>
              <div v-if="contestStarted" class="proctoring-banner"><Icon type="alert-circled" /> Proctoring active. Fullscreen required. Exits: {{ fullscreenExitCount }}/5</div>
              <div v-if="!contestStarted" v-html="contest.description" class="markdown-body"></div>
              <div v-else>
                <Table :columns="overviewColumns" :data="overviewRows" :loading="overviewLoading" border size="small"></Table>
              </div>
              <div v-if="passwordFormVisible && !contestStarted" class="contest-password">
                <Input v-model="contestPassword" type="password"
                       placeholder="contest password" class="contest-password-input"
                       @on-enter="checkPassword"/>
                <Button type="info" @click="checkPassword">Enter</Button>
              </div>
              
            </Panel>
            <Table v-if="!contestStarted" :columns="columns" :data="contest_table" disabled-hover style="margin-bottom: 12px;"></Table>
            <Alert v-if="contestStarted && !isFullscreen" type="warning" show-icon class="proctoring-warning">
              You exited full screen during contest. Please return to full screen. Warning {{ fullscreenExitCount }}/5
            </Alert>
          </div>
        </template>
      </div>

    </div>
    <!-- Contest menu removed from right side, now only shown in top navbar -->
  </div>
</template>

<script>
  import moment from 'moment'
  import api from '@oj/api'
  import { mapState, mapGetters, mapActions } from 'vuex'
  import { types } from '@/store'
  import { CONTEST_STATUS_REVERSE, CONTEST_STATUS } from '@/utils/constants'
  import time from '@/utils/time'

  export default {
    name: 'ContestDetail',
    components: {},
    data () {
      return {
        CONTEST_STATUS: CONTEST_STATUS,
        route_name: '',
        btnLoading: false,
        contestID: '',
        contestPassword: '',
        columns: [
          {
            title: this.$i18n.t('m.StartAt'),
            render: (h, params) => {
              return h('span', time.utcToLocal(params.row.start_time))
            }
          },
          {
            title: this.$i18n.t('m.EndAt'),
            render: (h, params) => {
              return h('span', time.utcToLocal(params.row.end_time))
            }
          },
          {
            title: this.$i18n.t('m.ContestType'),
            render: (h, params) => {
              return h('span', this.$i18n.t('m.' + params.row.contest_type ? params.row.contest_type.replace(' ', '_') : ''))
            }
          },
          {
            title: this.$i18n.t('m.Rule'),
            render: (h, params) => {
              return h('span', this.$i18n.t('m.' + params.row.rule_type))
            }
          },
          {
            title: this.$i18n.t('m.Creator'),
            render: (h, data) => {
              return h('span', data.row.created_by.username)
            }
          }
        ],
        overviewColumns: [
          { title: 'ID', key: 'problem_id', width: 80, align: 'center' },
          { title: 'Problem', key: 'problem_title' },
          { title: 'Status', key: 'best_result', align: 'center', render: (h, params) => {
              const r = params.row.best_result
              let text = 'NA'; let color = 'default'
              if (params.row.attempts > 0) {
                if (r === 0) { text = 'AC'; color = 'success' }
                else if (r === 8 || (params.row.passed_cases > 0 && params.row.passed_cases < params.row.total_cases)) { text = 'PC'; color = 'warning' }
                else { text = 'WA'; color = 'error' }
              }
              return h('Tag', { props: { color } }, text)
            }
          },
          { title: 'Total Submissions', key: 'attempts', width: 140, align: 'center' },
          { title: 'Score', key: 'score', width: 100, align: 'center' }
        ],
        overviewRows: [],
        overviewLoading: false,
        attemptId: null
      }
    },
    mounted () {
      this.contestID = this.$route.params.contestID
      this.route_name = this.$route.name
      
      // Restore contest state from localStorage if exists
      this.$store.dispatch('restoreContestState')
      
      this.$store.dispatch('getContest').then(res => {
        this.changeDomTitle({title: res.data.data.title})
        let data = res.data.data
        let endTime = moment(data.end_time)
        if (endTime.isAfter(moment(data.now))) {
          this.timer = setInterval(() => {
            this.$store.commit(types.NOW_ADD_1S)
          }, 1000)
        }
      })
      this.loadOverview()
      // Auto-refresh overview every 30 seconds
      this.overviewTimer = setInterval(() => {
        if (this.contestStarted) {
          this.loadOverview(true)
        }
      }, 30000)
    },
    beforeDestroy () {
      clearInterval(this.timer)
      clearInterval(this.overviewTimer)
      document.removeEventListener('fullscreenchange', this.onFullscreenChange)
      this.$store.commit(types.CLEAR_CONTEST)
    },
    methods: {
      ...mapActions(['changeDomTitle']),
      handleRoute (route) {
        this.$router.push(route)
      },
      handleStartContest () {
        this.$Modal.confirm({
          title: 'Start Contest',
          content: 'You will not be able to access other parts until you submit the contest. Are you sure to start?',
          onOk: () => {
            // Immediately set started state for instant UI update
            this.$store.commit(types.CONTEST_SET_STARTED, {started: true, resetCount: true, contestID: this.contestID})
            api.contestStart(this.contestID).then(res => {
              const attempt = res.data.data
              this.attemptId = attempt && attempt.id
              this.$store.state.contest.attempt = attempt
              // Save attempt to localStorage
              this.$store.commit(types.CONTEST_SET_STARTED, {started: true, contestID: this.contestID})
              this.loadOverview()
            }).catch(() => {})
            const el = document.documentElement
            if (el.requestFullscreen) {
              el.requestFullscreen()
            } else if (el.webkitRequestFullscreen) {
              el.webkitRequestFullscreen()
            } else if (el.mozRequestFullScreen) {
              el.mozRequestFullScreen()
            } else if (el.msRequestFullscreen) {
              el.msRequestFullscreen()
            }
            // Allow scrolling in fullscreen mode
            document.documentElement.style.overflow = 'auto'
            document.body.style.overflow = 'auto'
            this.$Modal.success({ title: 'All the best!', content: 'Contest started.' })
            this.$router.push({ name: 'contest-problem-list', params: { contestID: this.contestID } })
            document.addEventListener('fullscreenchange', this.onFullscreenChange)
            document.addEventListener('webkitfullscreenchange', this.onFullscreenChange)
            document.addEventListener('mozfullscreenchange', this.onFullscreenChange)
            document.addEventListener('MSFullscreenChange', this.onFullscreenChange)
          }
        })
      },
      handleStopContest () {
        const id = this.attemptId || (this.$store.state.contest.attempt && this.$store.state.contest.attempt.id)
        if (!id) {
          this.$Message.warning('No active contest attempt found')
          return
        }
        
        this.$Modal.confirm({
          title: 'Submit Contest',
          content: 'This will submit all your work and end the contest. Are you sure?',
          onOk: () => {
            // Submit all localStorage data to backend
            this.$store.dispatch('submitContestFromLocal', this.contestID).then(() => {
              this.$store.commit(types.CONTEST_RESET_LOCK, { contestID: this.contestID })
              document.documentElement.style.overflow = ''
              document.body.style.overflow = ''
              this.$Message.success('Contest submitted successfully')
              this.loadOverview()
            }).catch(() => {
              this.$Message.error('Failed to submit contest')
            })
          }
        })
      },
      onFullscreenChange () {
        const fs = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement
        // Ensure scroll is always enabled
        document.documentElement.style.overflow = 'auto'
        document.body.style.overflow = 'auto'
        
        if (!fs && this.contestStarted) {
          // Increment violation count
          this.$store.commit(types.CONTEST_INCREMENT_FULLSCREEN_EXIT, { contestID: this.contestID })
          
          // Wait for state to update, then process
          this.$nextTick(() => {
            const currentCount = this.fullscreenExitCount
            const id = this.attemptId || (this.$store.state.contest.attempt && this.$store.state.contest.attempt.id)
            
            console.log('Fullscreen exit detected. New count:', currentCount)
            
            // Save to backend immediately for admin monitoring
            if (id) {
              api.contestProctor(id, { 
                action: 'fullscreen_exit',
                violation_count: currentCount,
                timestamp: new Date().toISOString()
              }).then((res) => {
                console.log('Fullscreen exit recorded to backend:', res.data)
              }).catch((err) => {
                console.error('Failed to record fullscreen exit:', err)
              })
            } else {
              console.warn('No attempt ID found, violation not saved to backend')
            }
            
            // Show warning and prompt to return to fullscreen
            if (currentCount >= 5) {
              this.$Modal.error({
                title: 'Contest Auto-Submitted',
                content: `You have exited fullscreen ${currentCount} times. This is considered a violation. Your contest has been automatically submitted.`,
                onOk: () => {
                  // Auto-submit contest
                  this.$store.dispatch('submitContestFromLocal', this.contestID).then(() => {
                    this.$store.commit(types.CONTEST_RESET_LOCK, { contestID: this.contestID })
                    document.documentElement.style.overflow = ''
                    document.body.style.overflow = ''
                    this.$router.push({ name: 'contest-details', params: { contestID: this.contestID } })
                  }).catch(() => {
                    this.$Message.error('Failed to auto-submit contest')
                  })
                }
              })
            } else {
              // Show warning and re-prompt for fullscreen
              this.$Modal.warning({
                title: '⚠️ Fullscreen Exit Detected',
                content: `<div style="font-size: 14px; line-height: 1.6;">
                  <p><strong style="color: #ff6b6b;">Warning: Illegal Activity Detected!</strong></p>
                  <p>You have exited fullscreen mode.</p>
                  <p><strong>Violation Count: ${currentCount}/5</strong></p>
                  <p style="color: #666;">This action has been recorded and reported to the admin panel.</p>
                  <p style="color: #ff6b6b; font-weight: bold;">After 5 violations, your contest will be automatically submitted.</p>
                  <p style="margin-top: 10px;">Please click OK to return to fullscreen mode.</p>
                </div>`,
                okText: 'Return to Fullscreen',
                onOk: () => {
                  // Re-enable fullscreen
                  const el = document.documentElement
                  if (el.requestFullscreen) {
                    el.requestFullscreen().catch(() => {
                      this.$Message.error('Failed to enter fullscreen. Please press F11 or use browser fullscreen.')
                    })
                  } else if (el.webkitRequestFullscreen) {
                    el.webkitRequestFullscreen()
                  } else if (el.mozRequestFullScreen) {
                    el.mozRequestFullScreen()
                  } else if (el.msRequestFullscreen) {
                    el.msRequestFullscreen()
                  }
                  document.documentElement.style.overflow = 'auto'
                  document.body.style.overflow = 'auto'
                }
              })
            }
          })
        }
      },
      loadOverview (silent = false) {
        if (!silent) {
          this.overviewLoading = true
        }
        this.$store.dispatch('loadContestOverview').then(res => {
          const attempt = res.data.data
          if (attempt) {
            this.attemptId = attempt.id
            this.overviewRows = attempt.problem_stats || []
          } else {
            this.overviewRows = []
          }
          this.overviewLoading = false
        }).catch(() => { 
          this.overviewLoading = false 
        })
      },
      checkPassword () {
        if (this.contestPassword === '') {
          this.$error('Password can\'t be empty')
          return
        }
        this.btnLoading = true
        api.checkContestPassword(this.contestID, this.contestPassword).then((res) => {
          this.$success('Succeeded')
          this.$store.commit(types.CONTEST_ACCESS, {access: true})
          this.btnLoading = false
        }, (res) => {
          this.btnLoading = false
        })
      }
    },
    computed: {
      ...mapState({
        showMenu: state => state.contest.itemVisible.menu,
        contest: state => state.contest.contest,
        contest_table: state => [state.contest.contest],
        now: state => state.contest.now
      }),
      ...mapGetters(
        ['contestMenuDisabled', 'contestRuleType', 'contestStatus', 'countdown', 'isContestAdmin',
          'OIContestRealTimePermission', 'passwordFormVisible']
      ),
      contestStarted () { return this.$store.state.contest.started },
      fullscreenExitCount () { return this.$store.state.contest.fullscreenExitCount },
      isFullscreen () { return !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement) },
      countdownColor () {
        if (this.contestStatus) {
          return CONTEST_STATUS_REVERSE[this.contestStatus].color
        }
      },
      showAdminHelper () {
        return this.isContestAdmin && this.contestRuleType === 'ACM'
      }
    },
    watch: {
      '$route' (newVal) {
        this.route_name = newVal.name
        this.contestID = newVal.params.contestID
        this.changeDomTitle({title: this.contest.title})
      }
    }
  }
</script>

<style scoped lang="less">
  .countdown-actions {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .start-btn {
    background: #39ff14 !important;
    color: #000 !important;
    border: 1px solid #2fdc0b !important;
    box-shadow: 0 0 8px #39ff14;
  }
  .stop-btn { margin-left: 6px; }
  pre {
    display: inline-block;
  }
  #countdown {
    font-size: 16px;
  }

  .flex-container {
    #contest-main {
      flex: 1 1;
      width: 0;
      #contest-desc {
        flex: auto;
      }
    }
    #contest-menu {
      flex: none;
      width: 210px;
      margin-left: 20px;
    }
    .contest-password {
      margin-top: 20px;
      margin-bottom: -10px;
      &-input {
        width: 200px;
        margin-right: 10px;
      }
    }
  }
  .proctoring-banner {
    position: sticky;
    top: 70px;
    z-index: 10000;
    background: rgba(255, 243, 205, 0.95);
    color: #8a6d3b;
    border: 1px solid #faebcc;
    padding: 8px 12px;
    border-radius: 4px;
    margin-bottom: 8px;
  }
  .proctoring-warning { z-index: 10001; }
</style>
