import type { ComponentType } from "svelte";

export type Column = {
    key: string;
    header: string;
    sortable: boolean;
    filterable: boolean;
    component: ComponentType;
};

export function columnDef(key: string, header: string, sortable?: boolean, filterable?: boolean, component?: any): Column {
    return {
        key: key,
        header: header,
        sortable: sortable || false,
        filterable: filterable || false,
        component: component
    }
}

export function componentColumnDef(header: string, component: ComponentType): Column {
    return {
        key: '',
        header: header,
        sortable: false,
        filterable: false,
        component: component
    }
}