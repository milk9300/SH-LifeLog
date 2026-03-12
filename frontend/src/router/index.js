import { createRouter, createWebHistory } from 'vue-router'
import BrainstormPage from '../pages/BrainstormPage.vue'
import ProjectsPage from '../pages/ProjectsPage.vue'
import TimeHQPage from '../pages/TimeHQPage.vue'
import KnowledgePage from '../pages/KnowledgePage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import IncubationPage from '../pages/IncubationPage.vue'
import VaultPage from '../pages/VaultPage.vue'
import PlansPage from '../pages/PlansPage.vue'
import PlanDetailPage from '../pages/PlanDetailPage.vue'
import ArticlesPage from '../pages/ArticlesPage.vue'
import ArticleViewPage from '../pages/ArticleViewPage.vue'
import ArticleEditPage from '../pages/ArticleEditPage.vue'

/**
 * 路由配置
 * 定义应用的页面路由结构
 */
const routes = [
    {
        path: '/',
        name: 'Dashboard',
        component: DashboardPage,
        meta: { title: '工作台' }
    },
    {
        path: '/brainstorm',
        name: 'Brainstorm',
        component: BrainstormPage,
        meta: { title: '头脑风暴' }
    },
    {
        path: '/incubation',
        name: 'Incubation',
        component: IncubationPage,
        meta: { title: '产品验证实验室' }
    },
    {
        path: '/incubation/:id/flow',
        name: 'IncubationFlow',
        component: () => import('../pages/IncubationFlowPage.vue'),
        meta: { title: '项目向导流程', hideSidebar: true }
    },
    {
        path: '/projects',
        name: 'Projects',
        component: ProjectsPage,
        meta: { title: '项目大厅' }
    },
    {
        path: '/projects/:id',
        name: 'ProjectDetail',
        component: () => import('../pages/ProjectDetailPage.vue'),
        meta: { title: '项目详情' }
    },
    {
        path: '/plans',
        name: 'Plans',
        component: PlansPage,
        meta: { title: '长期计划' }
    },
    {
        path: '/plans/:id',
        name: 'PlanDetail',
        component: PlanDetailPage,
        meta: { title: '计划详情' }
    },
    {
        path: '/tasks',
        name: 'Tasks',
        component: TimeHQPage,
        meta: { title: '时间管理' }
    },
    {
        path: '/knowledge',
        name: 'Knowledge',
        component: KnowledgePage,
        meta: { title: '知识沉淀' }
    },
    {
        path: '/knowledge/:id/article-flow',
        name: 'ArticleFlow',
        component: () => import('../pages/ArticleFlowPage.vue'),
        meta: { title: '撰写技术文章', hideSidebar: true }
    },
    {
        path: '/articles',
        name: 'Articles',
        component: ArticlesPage,
        meta: { title: '文章管理' }
    },
    {
        path: '/articles/:id',
        name: 'ArticleView',
        component: ArticleViewPage,
        meta: { title: '查看文章', hideSidebar: true }
    },
    {
        path: '/articles/new',
        name: 'ArticleCreate',
        component: ArticleEditPage,
        meta: { title: '撰写新文章', hideSidebar: true }
    },
    {
        path: '/articles/:id/edit',
        name: 'ArticleEdit',
        component: ArticleEditPage,
        meta: { title: '编辑文章', hideSidebar: true }
    },
    {
        path: '/vault',
        name: 'Vault',
        component: VaultPage,
        meta: { title: '密码凭证' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫：更新页面标题
router.beforeEach((to, from, next) => {
    document.title = `${to.meta.title || 'Developer Dashboard'} - Developer Dashboard`
    next()
})

export default router
