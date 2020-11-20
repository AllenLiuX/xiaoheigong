import React, { useState, useEffect } from "react";
import axios from 'axios';
import Loading from 'react-simple-loading';
import queryString from 'query-string';
import router from "next/router"

export default function Article(props) {
    return (
        <div className="row mb-2 rowHover rounded">
            <div className="col-1 align-self-center">
                {props.source}
            </div>
            <div className="col-10">
                <div className="row">
                    {props.title}
                </div>
                <div className="row">
                    {props.date} 【{props.org_name}】
                </div>
            </div>
            <div className="col-1 align-self-center">
                <a href={props.download_url} target="_blank">LINK</a>
            </div>
        </div>
    )
}