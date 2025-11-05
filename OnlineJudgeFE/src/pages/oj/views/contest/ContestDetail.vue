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
              <div slot="extra">
                <Tag type="dot" :color="countdownColor">
                  <span id="countdown">{{countdown}}</span>
                </Tag>
              </div>
              <Alert v-if="contestStarted" type="success" show-icon style="margin-bottom: 10px;">
                Proctoring enabled: Fullscreen is required during the contest.
              </Alert>
              <div v-html="contest.description" class="markdown-body"></div>
              <div v-if="passwordFormVisible" class="contest-password">
                <Input v-model="contestPassword" type="password"
                       placeholder="contest password" class="contest-password-input"
                       @on-enter="checkPassword"/>
                <Button type="info" @click="checkPassword">Enter</Button>
              </div>
              <div style="margin-top: 12px;" v-if="!contestStarted">
                <Button type="primary" icon="play" @click="handleStartContest">Start Contest</Button>
              </div>
            </Panel>
            <Table :columns="columns" :data="contest_table" disabled-hover style="margin-bottom: 12px;"></Table>
            <Alert v-if="contestStarted && !isFullscreen" type="warning" show-icon>
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
        ]
      }
    },
    mounted () {
      this.contestID = this.$route.params.contestID
      this.route_name = this.$route.name
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
    },
    beforeDestroy () {
      clearInterval(this.timer)
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
            this.$store.commit(types.CONTEST_SET_STARTED, {started: true, resetCount: true})
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
            this.$Modal.success({ title: 'All the best!', content: 'Contest started.' })
            this.$router.push({ name: 'contest-problem-list', params: { contestID: this.contestID } })
            document.addEventListener('fullscreenchange', this.onFullscreenChange)
            document.addEventListener('webkitfullscreenchange', this.onFullscreenChange)
            document.addEventListener('mozfullscreenchange', this.onFullscreenChange)
            document.addEventListener('MSFullscreenChange', this.onFullscreenChange)
          }
        })
      },
      onFullscreenChange () {
        const fs = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement
        if (!fs && this.contestStarted) {
          this.$store.commit(types.CONTEST_INCREMENT_FULLSCREEN_EXIT)
          if (this.fullscreenExitCount >= 5) {
            this.$Modal.warning({ title: 'Contest submitted', content: 'You exited full screen 5 times. Submitting contest.' })
            this.$store.commit(types.CONTEST_RESET_LOCK)
            this.$router.push({ name: 'contest-details', params: { contestID: this.contestID } })
          }
        }
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
</style>
