import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IpamListComponent } from './components/ipam-list/ipam-list.component';
import { IpamDetailComponent } from './components/ipam-detail/ipam-detail.component';

const routes: Routes = [
    { path: '', component: IpamListComponent },
    { path: 'segment/:id', component: IpamDetailComponent }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class IpamRoutingModule { }
