import React, { lazy, Suspense } from 'react';
import { getBaseDomain } from 'core/utils/domain';

const HomeView = lazy(() => import('./HomeView'));
const PublicStorefront = lazy(() => import('modules/tienda/views/PublicStorefront'));

const RootView = () => {
    const hostname = window.location.hostname;
    const baseDomain = getBaseDomain(hostname);
    const isPublic = hostname === baseDomain;

    if (isPublic) {
        return <HomeView />;
    } else {
        return <PublicStorefront />;
    }
};

export default RootView;
