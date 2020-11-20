import React, { useState } from "react";
import Article from "./Article"

export default function Results(props) {
    return (
        <div className="col-7">
            <div className="row justify-content-center">
                <div className="col-11">
                    {props.articles.map((article, i) => {
                        return (
                            <Article
                                source={article.source}
                                title={article.title}
                                date={article.date}
                                org_name={article.org_name}
                                doc_type={article.doc_type}
                                download_url={article.download_url} />
                        )
                    })}
                </div>
            </div>
        </div>
    )
}